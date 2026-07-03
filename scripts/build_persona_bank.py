#!/usr/bin/env python3
"""Pre-generate the persona bank: one expanded student knowledge state per
misconception group found in the corpus (or per group named on the CLI).

Each persona is generated once by a strong model (Claude by default) and
cached to outputs/persona_bank.json; reruns only fill in missing groups.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from education_agents.evaluation.persona_bank import (
    DEFAULT_BANK_PATH,
    DEFAULT_PERSONA_MODEL,
    PersonaBank,
    render_knowledge_state,
)
from education_agents.evaluation.sim_corpus import load_corpus
from education_agents.evaluation.sim_v2 import build_item_batteries
from education_agents.facets import load_facet_map


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", default="confidence_intervals")
    parser.add_argument("--groups", default=None,
                        help="Comma-separated group keys (e.g. B15,B8+B10). "
                             "Default: every group in the corpus.")
    parser.add_argument("--model", default=None,
                        help=f"Persona-builder model (default: {DEFAULT_PERSONA_MODEL})")
    parser.add_argument("--bank", default=None,
                        help=f"Bank JSON path (default: {DEFAULT_BANK_PATH})")
    parser.add_argument("--rebuild", action="store_true",
                        help="Regenerate even if a group is already cached")
    parser.add_argument("--show", action="store_true",
                        help="Print each persona's rendered knowledge state")
    args = parser.parse_args()

    facet_map = load_facet_map(args.topic)
    bank = PersonaBank(args.bank)

    if args.groups:
        keys = [g.strip() for g in args.groups.split(",") if g.strip()]
    else:
        items = load_corpus(facet_map)
        batteries = build_item_batteries(items, facet_map)
        keys = sorted({key for b in batteries for key in b.persona_keys})
    print(f"{len(keys)} group(s); bank has {len(bank)} cached at {bank.path}")

    for key in keys:
        facet_ids = key.split("+")
        if args.rebuild and key in bank:
            del bank._records[key]
        cached = key in bank
        record = bank.get_or_build(facet_ids, facet_map, model=args.model)
        print(f"  {key:26s} {'cached' if cached else 'built '} ({record.model})")
        if args.show:
            print("  " + "-" * 58)
            print("  " + render_knowledge_state(record).replace("\n", "\n  "))
            print()

    print(f"\nBank saved: {bank.path} ({len(bank)} personas)")


if __name__ == "__main__":
    main()
