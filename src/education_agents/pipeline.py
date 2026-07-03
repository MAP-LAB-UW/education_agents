"""Top-level pipeline: generate items then judge them."""

from __future__ import annotations

import json
import time
from collections.abc import Iterator
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from .book_context import load_book_context
from .evaluation.correctness import evaluate_correctness
from .evaluation.facet_latency import evaluate_facet_latency
from .evaluation.figure_necessity import evaluate_figure_necessity
from .evaluation.figure_spoiler import evaluate_figure_spoiler
from .evaluation.naturalness import evaluate_naturalness
from .facets import load_facet_map
from .figures import execute_figures
from .generator import DEFAULT_GENERATOR_MODEL, generate_item, select_facets
from .judge import DEFAULT_JUDGE_MODEL, judge_item
from .schemas import EvalScores, GenerationRequest, RunArtifact

OUTPUTS_DIR = Path(__file__).resolve().parents[2] / "outputs"


DEFAULT_EVAL_MODEL = "anthropic/claude-sonnet-4-6"


def _forced_figure_indices(n_items: int, frac: float) -> set[int]:
    """Pick round(n_items * frac) item indices, spread evenly across the batch.

    Spreading (rather than taking the first k) keeps figure-required items
    interleaved with free ones, which matters because auto facet-selection
    accumulates history per item.
    """
    if frac <= 0 or n_items <= 0:
        return set()
    k = min(n_items, round(n_items * frac))
    if k <= 0:
        return set()
    return {round(j * n_items / k) for j in range(k)}


def run_stream(
    request: GenerationRequest,
    generator_model: str | None = None,
    judge_model: str | None = None,
    eval_model: str | None = None,
    output_dir: Path | None = None,
    skip_eval: bool = False,
    skip_judge: bool = False,
) -> Iterator[RunArtifact]:
    """Generate, judge, and (optionally) evaluate items one at a time.

    Yields each ``RunArtifact`` as soon as it is produced and written to disk,
    so callers (e.g. the web dashboard) can surface items incrementally rather
    than waiting for the whole batch to finish.
    """
    gen_model = generator_model or DEFAULT_GENERATOR_MODEL
    jdg_model = judge_model or DEFAULT_JUDGE_MODEL
    evl_model = eval_model or DEFAULT_EVAL_MODEL
    out_dir = output_dir or OUTPUTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    facet_map = load_facet_map(request.topic)
    book_context = load_book_context(request.book_context_mode)

    previously_used_facets: list[list[str]] = []
    forced_figure_idx = _forced_figure_indices(
        request.n_items, request.min_frac_with_figures
    )

    for i in range(request.n_items):
        force_figure = i in forced_figure_idx
        current_request = request
        selection_reasoning = None
        if request.auto_select_facets:
            selection = select_facets(
                facet_map, previously_used_facets, model=gen_model
            )
            selection_reasoning = selection.reasoning
            print(
                f"[{i + 1}/{request.n_items}] auto-selected facets: "
                f"{', '.join(selection.target_facets)}  "
                f"({selection_reasoning})"
            )
            current_request = request.model_copy(
                update={"target_facets": selection.target_facets}
            )

        t0 = time.time()
        item = generate_item(
            current_request, facet_map, book_context, model=gen_model,
            force_figure=force_figure,
        )
        # A figure-required item that came back figure-less gets one retry —
        # the model occasionally ignores the instruction.
        if force_figure and not item.figures:
            print(f"[{i + 1}/{request.n_items}] figure required but none "
                  f"produced — retrying once")
            item = generate_item(
                current_request, facet_map, book_context, model=gen_model,
                force_figure=True,
            )
        gen_time = time.time() - t0

        figure_data: dict[str, str] = {}
        if item.figures:
            figure_data = execute_figures(item.figures)
            print(
                f"[{i + 1}/{request.n_items}] rendered {len(figure_data)}/{len(item.figures)} figures"
            )

        report = None
        judge_time = 0.0
        if not skip_judge:
            t1 = time.time()
            report = judge_item(item, facet_map, model=jdg_model, figure_data=figure_data)
            judge_time = time.time() - t1

        eval_scores = None
        eval_time = 0.0
        if not skip_eval:
            t2 = time.time()
            correctness = evaluate_correctness(item, model=evl_model, figure_data=figure_data)
            naturalness = evaluate_naturalness(item, model=evl_model, figure_data=figure_data)
            latency = evaluate_facet_latency(item, facet_map)
            fig_necessity = None
            fig_spoiler = None
            if figure_data:
                fig_nec = evaluate_figure_necessity(item, model=evl_model)
                fig_necessity = int(fig_nec.is_necessary)
                fig_spl = evaluate_figure_spoiler(item, figure_data, model=evl_model)
                fig_spoiler = int(fig_spl.gives_away_answer)
            eval_scores = EvalScores(
                correctness_pass=correctness.is_correct,
                correctness_flagged_distractors=correctness.flagged_distractors,
                naturalness_stem=naturalness.stem_score,
                naturalness_options=naturalness.options_score,
                naturalness_overall=naturalness.overall_score,
                latency_score=latency.score,
                latency_similarity=latency.mean_similarity,
                latency_bucket=latency.bucket,
                latency_option_details=[od.model_dump() for od in latency.option_details],
                figure_necessity=fig_necessity,
                figure_spoiler=fig_spoiler,
            )
            eval_time = time.time() - t2

        now = datetime.now(timezone.utc)
        timestamp = now.strftime("%Y%m%dT%H%M%S")
        short_hash = sha256(
            f"{timestamp}-{i}".encode()
        ).hexdigest()[:8]

        previously_used_facets.append(current_request.target_facets)

        timing = {"generator_s": round(gen_time, 2)}
        if not skip_judge:
            timing["judge_s"] = round(judge_time, 2)
        if not skip_eval:
            timing["eval_s"] = round(eval_time, 2)

        artifact = RunArtifact(
            request=current_request,
            models={"generator": gen_model, "judge": jdg_model},
            facet_selection_reasoning=selection_reasoning,
            item=item,
            judge_report=report,
            eval_scores=eval_scores,
            figure_data=figure_data,
            timing=timing,
            created_at=now.isoformat(),
        )

        out_path = out_dir / f"{timestamp}_{short_hash}.json"
        out_path.write_text(
            json.dumps(artifact.model_dump(), indent=2, ensure_ascii=False)
        )
        eval_info = ""
        if eval_scores:
            eval_info = (
                f", correct={'Y' if eval_scores.correctness_pass else 'N'}"
                f", natural={eval_scores.naturalness_overall}/5"
                f", latency={eval_scores.latency_score}/4"
            )
        judge_info = (
            f", judge={judge_time:.1f}s, agreement={report.overall_agreement:.0%}"
            if report is not None else ", judge=skipped"
        )
        print(
            f"[{i + 1}/{request.n_items}] saved {out_path.name}  "
            f"(gen={gen_time:.1f}s{judge_info}"
            f"{', eval=' + f'{eval_time:.1f}s' if not skip_eval else ''})"
        )

        yield artifact


def run(
    request: GenerationRequest,
    generator_model: str | None = None,
    judge_model: str | None = None,
    eval_model: str | None = None,
    output_dir: Path | None = None,
    skip_eval: bool = False,
    skip_judge: bool = False,
) -> list[RunArtifact]:
    """Generate and judge a batch of items, returning all artifacts at once."""
    return list(
        run_stream(
            request,
            generator_model=generator_model,
            judge_model=judge_model,
            eval_model=eval_model,
            output_dir=output_dir,
            skip_eval=skip_eval,
            skip_judge=skip_judge,
        )
    )
