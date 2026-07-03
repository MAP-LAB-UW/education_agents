#!/usr/bin/env python3
"""Local server for the Diagnostic Assessment Copilot dashboard.

Serves the static dashboard (``web/``) *and* exposes a generation backend so the
"Generate" button in the dashboard actually produces items, instead of only
loading pre-computed artifacts from disk.

It is a thin wrapper over :func:`education_agents.pipeline.run_stream`: the
``POST /api/generate`` endpoint streams newline-delimited JSON (NDJSON), one
``RunArtifact`` per line, as each item is generated and judged. The browser
reads the stream and appends items live.

Run it from the repo root:

    conda run -n education-env python scripts/serve_dashboard.py

then open http://localhost:8000/web/index.html

Requires an ``ANTHROPIC_API_KEY`` (the default generator/judge models are
Claude). Set it in a ``.env`` file at the repo root or in the environment —
or just start the server: if no key is detected, the dashboard prompts for
one on load and can persist it to ``.env`` for future sessions.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
import urllib.error
import urllib.request
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from education_agents.facets import load_facet_map  # noqa: E402
from education_agents.pipeline import run_stream  # noqa: E402
from education_agents.schemas import GeneratedItem, GenerationRequest  # noqa: E402

# Dashboard generation defaults. Opus 4.6 drafts items; Sonnet 4.6 judges them
# (Opus as judge is accurate but too slow for the interactive dashboard).
# Both are overridable per-request from the dashboard's model selectors.
DEFAULT_GENERATOR_MODEL = "anthropic/claude-opus-4-6"
DEFAULT_JUDGE_MODEL = "anthropic/claude-sonnet-4-6"
# The correctness rubric solves items blind; Sonnet keeps it fast.
DEFAULT_EVAL_MODEL = "anthropic/claude-sonnet-4-6"

# Models offered in the dashboard's generator/judge selectors.
MODEL_CHOICES = [
    "anthropic/claude-opus-4-6",
    "anthropic/claude-sonnet-4-6",
    "anthropic/claude-haiku-4-5",
]

# Items generated from the dashboard are written here so they can be reloaded.
WEB_OUTPUT_DIR = REPO_ROOT / "outputs" / "web_generated"

ENV_FILE = REPO_ROOT / ".env"
ANTHROPIC_KEY_VAR = "ANTHROPIC_API_KEY"


def _has_anthropic_key() -> bool:
    return bool(os.environ.get(ANTHROPIC_KEY_VAR, "").strip())


def _verify_anthropic_key(api_key: str) -> tuple[bool | None, str]:
    """Check a key against the Anthropic API without spending tokens.

    Returns (valid, detail). ``valid`` is None when the check itself failed
    (e.g. no network), in which case the key is accepted unverified.
    """
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/models",
        headers={"x-api-key": api_key, "anthropic-version": "2023-06-01"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10):
            return True, "Key verified with the Anthropic API."
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            return False, "The Anthropic API rejected this key."
        return None, f"Could not verify the key (HTTP {exc.code}); saved unverified."
    except (urllib.error.URLError, TimeoutError):
        return None, "Could not reach the Anthropic API; key saved unverified."


def _persist_key_to_env_file(api_key: str) -> None:
    """Write/replace the ANTHROPIC_API_KEY line in the repo-root .env file."""
    line = f"{ANTHROPIC_KEY_VAR}={api_key}"
    if ENV_FILE.exists():
        lines = ENV_FILE.read_text(encoding="utf-8").splitlines()
        replaced = False
        for i, existing in enumerate(lines):
            if existing.strip().startswith(f"{ANTHROPIC_KEY_VAR}="):
                lines[i] = line
                replaced = True
                break
        if not replaced:
            lines.append(line)
        content = "\n".join(lines) + "\n"
    else:
        content = line + "\n"
    ENV_FILE.write_text(content, encoding="utf-8")
    try:
        ENV_FILE.chmod(0o600)
    except OSError:
        pass


def _parse_items(payload: dict) -> list[tuple[str, GeneratedItem, dict]]:
    """Pull (source, GeneratedItem, figure_data) tuples out of a dashboard payload.

    Accepts the same artifact shape the dashboard holds in memory (the output of
    ``RunArtifact.model_dump()``), tolerating artifacts that are missing the
    surrounding pipeline metadata.
    """
    items: list[tuple[str, GeneratedItem, dict]] = []
    for idx, raw in enumerate(payload.get("artifacts", [])):
        if not isinstance(raw, dict) or "item" not in raw:
            continue
        item = GeneratedItem.model_validate(raw["item"])
        figure_data = raw.get("figure_data") or {}
        source = (raw.get("created_at") or "")[:19] or f"item_{idx + 1}"
        items.append((source, item, figure_data))
    return items


def _agreement_maps(payload: dict) -> list[dict[str, str]]:
    """Per-item {option_id: judge agreement} maps, aligned 1:1 with _parse_items.

    Uses the identical artifact filter so list positions match the items the
    rest of the simulate flow indexes by.
    """
    maps: list[dict[str, str]] = []
    for raw in payload.get("artifacts", []):
        if not isinstance(raw, dict) or "item" not in raw:
            continue
        assessments = (raw.get("judge_report") or {}).get("option_assessments", [])
        maps.append({
            oa.get("option_id"): oa.get("agreement")
            for oa in assessments if isinstance(oa, dict)
        })
    return maps


class _ItemShim:
    """Minimal stand-in exposing ``.item`` for corpus rubrics that only need it."""

    __slots__ = ("item",)

    def __init__(self, item: GeneratedItem) -> None:
        self.item = item


def _as_artifacts(items: list[tuple[str, GeneratedItem, dict]]) -> list[_ItemShim]:
    return [_ItemShim(item) for _, item, _ in items]


def _build_request(payload: dict) -> GenerationRequest:
    """Translate the dashboard's JSON config into a GenerationRequest."""
    facets = payload.get("target_facets") or []
    # Auto-select mode sends an empty facet list (GenerationRequest treats an
    # empty target_facets as "let the model choose").
    if payload.get("auto_select_facets"):
        facets = []

    return GenerationRequest(
        topic=payload.get("topic", "confidence_intervals"),
        target_facets=facets,
        response_format=payload.get("response_format"),
        num_options=payload.get("num_options"),
        book_context_mode=payload.get("book_context_mode", "none"),
        n_items=int(payload.get("n_items", 1)),
        exclude_image_examples=payload.get("exclude_image_examples", True),
        prompt_version=payload.get("prompt_version", "v3"),
        min_frac_with_figures=float(payload.get("min_frac_with_figures", 0.0)),
    )


class DashboardHandler(SimpleHTTPRequestHandler):
    """Serves static files from the repo root and handles the generate API."""

    # SimpleHTTPRequestHandler is instantiated per-request; `directory` is bound
    # via functools.partial in `main`.

    def _send_json(self, status: int, obj: dict) -> None:
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _start_ndjson(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()

    def _write_frame(self, frame: dict) -> None:
        self.wfile.write((json.dumps(frame) + "\n").encode("utf-8"))
        self.wfile.flush()

    def _read_payload(self) -> dict | None:
        try:
            length = int(self.headers.get("Content-Length", 0))
            return json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError) as exc:
            self._send_json(400, {"error": f"Invalid request body: {exc}"})
            return None

    def do_GET(self) -> None:  # noqa: N802 (stdlib naming)
        if self.path.rstrip("/") == "/api/config":
            self._send_json(
                200,
                {
                    "generator_model": DEFAULT_GENERATOR_MODEL,
                    "judge_model": DEFAULT_JUDGE_MODEL,
                    "eval_model": DEFAULT_EVAL_MODEL,
                    "model_choices": MODEL_CHOICES,
                    "has_anthropic_key": _has_anthropic_key(),
                },
            )
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802 (stdlib naming)
        path = self.path.rstrip("/")
        if path == "/api/generate":
            self._handle_generate()
        elif path == "/api/key":
            self._handle_set_key()
        elif path == "/api/evaluate":
            self._handle_evaluate()
        elif path == "/api/simulate":
            self._handle_simulate()
        else:
            self._send_json(404, {"error": f"No such endpoint: {self.path}"})

    def _handle_set_key(self) -> None:
        """Accept an Anthropic API key from the dashboard.

        The key is verified against the Anthropic API (a token-free models
        list call), set in this process's environment so subsequent litellm
        calls pick it up, and optionally persisted to the repo-root ``.env``
        (which is gitignored) so future sessions don't have to re-enter it.
        Only reachable from the loopback bind this server defaults to.
        """
        payload = self._read_payload()
        if payload is None:
            return

        api_key = (payload.get("api_key") or "").strip()
        if not api_key:
            self._send_json(400, {"error": "No API key provided."})
            return
        if any(c.isspace() for c in api_key):
            self._send_json(400, {"error": "API keys cannot contain whitespace."})
            return

        valid, detail = _verify_anthropic_key(api_key)
        if valid is False:
            self._send_json(401, {"error": detail})
            return

        os.environ[ANTHROPIC_KEY_VAR] = api_key
        persisted = False
        if payload.get("persist", True):
            try:
                _persist_key_to_env_file(api_key)
                persisted = True
            except OSError as exc:
                detail = f"{detail} Could not write .env: {exc}"

        self._send_json(200, {
            "ok": True,
            "verified": valid is True,
            "persisted": persisted,
            "detail": detail,
        })

    def _handle_generate(self) -> None:
        payload = self._read_payload()
        if payload is None:
            return

        try:
            request = _build_request(payload)
        except Exception as exc:  # pydantic validation, bad enum values, etc.
            self._send_json(400, {"error": f"Invalid generation request: {exc}"})
            return

        generator_model = payload.get("generator_model") or DEFAULT_GENERATOR_MODEL
        judge_model = payload.get("judge_model") or DEFAULT_JUDGE_MODEL
        skip_eval = not payload.get("run_eval", False)
        skip_judge = bool(payload.get("skip_judge", False))

        # Stream NDJSON: one JSON object per line. The first line is a "meta"
        # frame, then one "item" frame per artifact, then a terminal "done"
        # (or "error") frame.
        self._start_ndjson()
        self._write_frame({
            "type": "meta",
            "n_items": request.n_items,
            "generator_model": generator_model,
            "judge_model": judge_model if not skip_judge else None,
            "auto_select_facets": request.auto_select_facets,
            "skip_judge": skip_judge,
        })

        count = 0
        try:
            stream = run_stream(
                request,
                generator_model=generator_model,
                judge_model=judge_model,
                output_dir=WEB_OUTPUT_DIR,
                skip_eval=skip_eval,
                skip_judge=skip_judge,
            )
            for artifact in stream:
                count += 1
                self._write_frame({
                    "type": "item",
                    "index": count,
                    "artifact": artifact.model_dump(),
                })
            self._write_frame({"type": "done", "count": count})
        except BrokenPipeError:
            # Client navigated away / cancelled — nothing more to do.
            return
        except Exception as exc:
            traceback.print_exc()
            try:
                self._write_frame({"type": "error", "message": str(exc), "completed": count})
            except BrokenPipeError:
                pass

    def _handle_evaluate(self) -> None:
        """Run the requested rubrics over the items the dashboard is showing.

        Per item: correctness (a strong model solves blind) and facet latency
        (embedding distance between options and the facets they claim to encode).
        Corpus-level: semantic diversity (stem similarity among items and against
        the expert examples) and facet coverage.
        """
        # Imported lazily: loading sentence-transformers / torch is slow, and a
        # generate-only session should never pay that cost.
        from education_agents.evaluation.correctness import evaluate_correctness
        from education_agents.evaluation.corpus_metrics import (
            evaluate_facet_coverage,
            evaluate_facet_qmatrix_diversity,
            evaluate_semantic_diversity,
            evaluate_similarity_with_experts,
        )
        from education_agents.evaluation.facet_latency import (
            _get_model,
            evaluate_facet_latency,
        )

        payload = self._read_payload()
        if payload is None:
            return

        try:
            items = _parse_items(payload)
        except Exception as exc:
            self._send_json(400, {"error": f"Could not parse items: {exc}"})
            return

        if not items:
            self._send_json(400, {"error": "No items to evaluate."})
            return

        topic = payload.get("topic", "confidence_intervals")
        eval_model = payload.get("eval_model") or DEFAULT_EVAL_MODEL

        self._start_ndjson()
        self._write_frame({"type": "meta", "n_items": len(items), "eval_model": eval_model})

        try:
            facet_map = load_facet_map(topic)
            embed_model = _get_model()

            stems = [item.stem for _, item, _ in items]
            options = [[o.text for o in item.options] for _, item, _ in items]
            sources = [src for src, _, _ in items]

            # Per-item rubrics, streamed as each finishes.
            latency_results = []
            for index, (source, item, figure_data) in enumerate(items, start=1):
                correctness = evaluate_correctness(
                    item, model=eval_model, figure_data=figure_data
                )
                latency = evaluate_facet_latency(item, facet_map, model=embed_model)
                latency_results.append(latency)
                eval_scores = {
                    "correctness_pass": correctness.is_correct,
                    "correctness_flagged_distractors": correctness.flagged_distractors,
                    "correctness_selected_answer": correctness.selected_answer,
                    "latency_score": latency.score,
                    "latency_similarity": latency.mean_similarity,
                    "latency_bucket": latency.bucket,
                    "latency_option_details": [od.model_dump() for od in latency.option_details],
                }
                # Figure spoiler: only meaningful when the item actually has a
                # rendered figure. Detects the opposite failure of decorative
                # figures — a figure that leaks the answer via its labels.
                if figure_data:
                    from education_agents.evaluation.figure_spoiler import (
                        evaluate_figure_spoiler,
                    )
                    spoiler = evaluate_figure_spoiler(
                        item, figure_data, model=eval_model
                    )
                    eval_scores["figure_spoiler"] = int(spoiler.gives_away_answer)
                    eval_scores["figure_spoiler_leaked_via"] = (
                        spoiler.trials[0].leaked_via if spoiler.trials else ""
                    )
                self._write_frame({
                    "type": "item",
                    "index": index,
                    "source": source,
                    "eval_scores": eval_scores,
                })

            # Corpus-level rubrics: semantic diversity (within-corpus + vs experts)
            # and facet coverage.
            expert_stems = [ex.stem for ex in facet_map.examples]
            expert_ids = [f"expert_{i + 1}" for i in range(len(expert_stems))]
            expert_options = [[o.text for o in ex.options] for ex in facet_map.examples]
            expert_sims = evaluate_similarity_with_experts(
                stems, sources, options=options,
                reference_stems=expert_stems or None,
                reference_ids=expert_ids or None,
                reference_options=expert_options or None,
                embed_model=embed_model,
            )
            for index, sim in enumerate(expert_sims, start=1):
                self._write_frame({
                    "type": "expert_similarity",
                    "index": index,
                    "similarity_with_experts": sim.model_dump(),
                })

            coverage = evaluate_facet_coverage(_as_artifacts(items), facet_map)
            among = evaluate_semantic_diversity(
                _as_artifacts(items), embed_model=embed_model
            ).model_dump()
            qmatrix = evaluate_facet_qmatrix_diversity(
                _as_artifacts(items), facet_map
            ).model_dump()
            # Mean over items of each item's *closest*-expert similarity (max
            # match), so the corpus card leads with the same statistic as the
            # per-item card.
            max_expert = (
                round(sum(s.max_similarity for s in expert_sims) / len(expert_sims), 4)
                if expert_sims else 0.0
            )

            self._write_frame({
                "type": "corpus",
                "corpus": {
                    "facet_coverage": coverage.model_dump(),
                    "semantic_diversity": among,
                    "facet_qmatrix_diversity": qmatrix,
                    "expert_similarity_max": max_expert,
                    "n_expert_refs": len(expert_stems),
                },
            })
            self._write_frame({"type": "done", "count": len(items)})
        except BrokenPipeError:
            return
        except Exception as exc:
            traceback.print_exc()
            try:
                self._write_frame({"type": "error", "message": str(exc)})
            except BrokenPipeError:
                pass

    def _handle_simulate(self) -> None:
        """Run the student simulator (v2) over dashboard items.

        Per item: one persona per misconception group keyed to its incorrect
        options (one misconception at a time), plus a no-misconception control.
        Each persona answers the stem open-mode; a blind mapper resolves the
        free answer to an option (with a select-mode fallback when nothing
        matches); a blind lineup judge says which misconception the reasoning
        exhibits. Streams one NDJSON frame per persona run.
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        from education_agents.evaluation.persona_bank import PersonaBank
        from education_agents.evaluation.sim_corpus import SimItem, SimOption
        from education_agents.evaluation.sim_v2 import (
            CONTROL_KEY,
            DEFAULT_JUDGE_MODEL,
            DEFAULT_MAPPER_MODEL,
            DEFAULT_V2_STUDENT_MODEL,
            ItemBattery,
            battery_run_plan,
            build_item_batteries,
            effective_option_ids,
            run_attempt,
        )

        payload = self._read_payload()
        if payload is None:
            return

        try:
            items = _parse_items(payload)
        except Exception as exc:
            self._send_json(400, {"error": f"Could not parse items: {exc}"})
            return
        if not items:
            self._send_json(400, {"error": "No items to simulate."})
            return

        indices = payload.get("indices")  # 0-based; None -> all items
        wanted = set(indices) if indices is not None else None
        k = max(1, int(payload.get("k", 1)))
        topic = payload.get("topic", "confidence_intervals")
        student_model = payload.get("student_model") or DEFAULT_V2_STUDENT_MODEL
        # Only simulate distractors whose misconception keying the judge agrees
        # with (per-option agreement == "match"); disagreed keyings make the
        # simulation premise unreliable. Default on; override with the flag.
        require_agreement = payload.get("require_agreement", True)
        agreement_maps = _agreement_maps(payload) if require_agreement else None

        facet_map = load_facet_map(topic)

        # Index-tagged SimItems so frames can be merged back client-side.
        sim_items = []
        for idx, (_, item, figure_data) in enumerate(items):
            if wanted is not None and idx not in wanted:
                continue
            sim_items.append(SimItem(
                source=f"item_{idx}",
                stem=item.stem,
                response_format=item.response_format,
                options=[
                    SimOption(id=o.id, text=o.text, facet_tags=o.facet_tags,
                              is_correct=o.is_correct)
                    for o in item.options
                ],
                figure_data=figure_data or {},
            ))

        batteries = {
            int(b.item.source.split("_")[1]): b
            for b in build_item_batteries(sim_items, facet_map)
        }

        # Filter each battery's targets to options the judge agrees on.
        skip_reasons: dict[int, str] = {}
        dropped_targets: dict[int, list[str]] = {}
        if require_agreement:
            for idx, battery in list(batteries.items()):
                amap = agreement_maps[idx] if idx < len(agreement_maps) else {}
                # No judge assessments at all (e.g. judging was skipped) -> no
                # agreement info to filter on, so simulate every target.
                if not amap:
                    continue
                kept = [t for t in battery.targets
                        if amap.get(t.option_id) == "match"]
                dropped = [t.option_id for t in battery.targets if t not in kept]
                if not kept:
                    del batteries[idx]
                    skip_reasons[idx] = (
                        "Generator and judge do not agree on the misconception "
                        "keying of any distractor (no option assessed as a match), "
                        "so the simulation premise can't be trusted here."
                    )
                    continue
                if dropped:
                    dropped_targets[idx] = dropped
                batteries[idx] = ItemBattery(
                    item=battery.item, targets=kept,
                    persona_keys=sorted({t.group_key for t in kept}),
                )

        self._start_ndjson()
        self._write_frame({
            "type": "meta",
            "n_items": len(sim_items),
            "k": k,
            "student_model": student_model,
            "mapper_model": DEFAULT_MAPPER_MODEL,
            "judge_model": DEFAULT_JUDGE_MODEL,
        })

        try:
            bank = PersonaBank()
            needed = sorted({key for b in batteries.values() for key in b.persona_keys})
            for key in needed:
                if key not in bank:
                    self._write_frame({"type": "status",
                                       "message": f"Building persona {key}…"})
                    bank.get_or_build(key.split("+"), facet_map)

            for si in sim_items:
                idx = int(si.source.split("_")[1])
                battery = batteries.get(idx)
                if battery is None:
                    self._write_frame({
                        "type": "item_skipped", "item_index": idx,
                        "reason": skip_reasons.get(
                            idx,
                            "No incorrect option is keyed to a misconception facet.",
                        ),
                    })
                    continue

                if dropped_targets.get(idx):
                    self._write_frame({
                        "type": "item_note", "item_index": idx,
                        "message": (
                            "Skipped distractor(s) "
                            f"{', '.join(dropped_targets[idx])} — generator and "
                            "judge disagree on their misconception keying."
                        ),
                    })

                correct_ids = sorted(o.id for o in battery.item.options if o.is_correct)
                plan = battery_run_plan(battery, k)

                def _one(pk, sample):
                    return run_attempt(
                        battery, pk, sample, bank, facet_map,
                        student_model=student_model,
                    )

                with ThreadPoolExecutor(max_workers=4) as pool:
                    futures = [pool.submit(_one, pk, s) for pk, s in plan]
                    for fut in as_completed(futures):
                        try:
                            a = fut.result()
                        except Exception as exc:
                            traceback.print_exc()
                            self._write_frame({"type": "attempt_error",
                                               "item_index": idx, "message": str(exc)})
                            continue
                        selected = effective_option_ids(a)
                        if a.persona_key == CONTROL_KEY:
                            targets = correct_ids
                            hit = sorted(selected) == correct_ids
                        else:
                            targets = sorted(t.option_id for t in battery.targets
                                             if t.group_key == a.persona_key)
                            hit = any(t in selected for t in targets)
                        self._write_frame({
                            "type": "attempt",
                            "item_index": idx,
                            "attempt": a.model_dump(),
                            "selected_ids": selected,
                            "target_option_ids": targets,
                            "hit": hit,
                            "is_control": a.persona_key == CONTROL_KEY,
                        })
                self._write_frame({"type": "item_done", "item_index": idx})

            self._write_frame({"type": "done", "count": len(sim_items)})
        except BrokenPipeError:
            return
        except Exception as exc:
            traceback.print_exc()
            try:
                self._write_frame({"type": "error", "message": str(exc)})
            except BrokenPipeError:
                pass

    def log_message(self, fmt: str, *args) -> None:
        # Keep API noise readable; suppress the per-static-file access spam.
        if "/api/" in self.path:
            super().log_message(fmt, *args)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000, help="Port to serve on")
    parser.add_argument("--host", default="127.0.0.1", help="Host/interface to bind")
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not open the dashboard in a browser on startup",
    )
    args = parser.parse_args()

    handler = partial(DashboardHandler, directory=str(REPO_ROOT))
    server = ThreadingHTTPServer((args.host, args.port), handler)

    url = f"http://{args.host}:{args.port}/web/index.html"
    print(f"Diagnostic Assessment Copilot — dashboard server")
    print(f"  Serving {REPO_ROOT}")
    print(f"  Generator: {DEFAULT_GENERATOR_MODEL}")
    print(f"  Judge:     {DEFAULT_JUDGE_MODEL}")
    print(f"  Eval:      {DEFAULT_EVAL_MODEL}  (correctness; latency/diversity use embeddings)")
    if not _has_anthropic_key():
        print(f"  Note: no {ANTHROPIC_KEY_VAR} detected — the dashboard will ask for one.")
    print(f"  Open: {url}")
    print("  Press Ctrl+C to stop.")

    if not args.no_open:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.shutdown()


if __name__ == "__main__":
    main()
