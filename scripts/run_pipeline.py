#!/usr/bin/env python3
"""CLI for the diagnostic assessment pipeline."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from education_agents.pipeline import run
from education_agents.schemas import GenerationRequest


def main():
    parser = argparse.ArgumentParser(
        description="Generate and judge diagnostic assessment items."
    )
    parser.add_argument(
        "--topic",
        default="confidence_intervals",
        help="Topic name (matches data/facets/<topic>.json)",
    )
    parser.add_argument(
        "--facets",
        nargs="*",
        default=[],
        help="Target facet IDs, e.g. A4 B15 B16. Omit to let the model auto-select.",
    )
    parser.add_argument(
        "--format",
        dest="response_format",
        default=None,
        choices=["single_select", "multi_select", "true_false_per_option"],
        help="Response format. Omit to let the model choose.",
    )
    parser.add_argument(
        "--num-options",
        type=int,
        default=None,
        help="Number of options per item. Omit to let the model choose.",
    )
    parser.add_argument(
        "--book-mode",
        default="none",
        choices=["none", "full_tex", "rag"],
        help="Book context mode",
    )
    parser.add_argument(
        "--n-items", type=int, default=1, help="Number of items to generate"
    )
    parser.add_argument(
        "--include-image-examples",
        action="store_true",
        help="Include image-based examples in few-shot prompt (excluded by default)",
    )
    parser.add_argument(
        "--prompt-version",
        default="v2",
        choices=["v1", "v2", "v3"],
        help="Generator prompt version: v1 (original), v2 (latent-facet), v3 (LaTeX + figures)",
    )
    parser.add_argument(
        "--generator-model",
        default=None,
        help="Override generator model (default: gemini/gemini-3-flash-preview)",
    )
    parser.add_argument(
        "--judge-model",
        default=None,
        help="Override judge model (default: gemini/gemini-3.1-pro-preview)",
    )
    parser.add_argument(
        "--eval-model",
        default=None,
        help="Override eval model (default: gemini/gemini-3.1-pro-preview)",
    )
    parser.add_argument(
        "--skip-eval",
        action="store_true",
        help="Skip evaluation rubrics (only run generation + judge)",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Output directory (default: outputs/)",
    )

    args = parser.parse_args()

    request = GenerationRequest(
        topic=args.topic,
        target_facets=args.facets,
        response_format=args.response_format,
        num_options=args.num_options,
        book_context_mode=args.book_mode,
        n_items=args.n_items,
        exclude_image_examples=not args.include_image_examples,
        prompt_version=args.prompt_version,
    )

    out_dir = Path(args.out) if args.out else None

    print(f"Topic: {request.topic}")
    if request.auto_select_facets:
        print("Target facets: auto (model will select per item)")
    else:
        print(f"Target facets: {', '.join(request.target_facets)}")
    fmt = request.response_format or "auto (model will choose)"
    opts = str(request.num_options) if request.num_options else "auto (model will choose)"
    print(f"Format: {fmt}, {opts} options")
    print(f"Book context: {request.book_context_mode}")
    print(f"Items to generate: {request.n_items}")
    print()

    artifacts = run(
        request,
        generator_model=args.generator_model,
        judge_model=args.judge_model,
        eval_model=args.eval_model,
        output_dir=out_dir,
        skip_eval=args.skip_eval,
    )

    print(f"\nDone. Generated {len(artifacts)} item(s).")
    for a in artifacts:
        r = a.judge_report
        print(
            f"  agreement={r.overall_agreement:.0%}  "
            f"confidence={r.overall_confidence:.2f}  "
            f"issues={len(r.issues)}"
        )


if __name__ == "__main__":
    main()
