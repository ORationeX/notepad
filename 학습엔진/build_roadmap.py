# -*- coding: utf-8 -*-
"""Build and verify modular roadmaps from the `curriculum` package.

Usage:
    python build_roadmap.py                    # Build roadmap/*.json and run order checks
    python build_roadmap.py --verify --tree    # Print hierarchy and run structural verification
    python build_roadmap.py --verify --track en --unit u3
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from curriculum.builder import TRACK_IDS, build_all, check_order, write_roadmap
from curriculum.verify import main as verify_main


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build roadmap/*.json or run scoped curriculum verification.")
    parser.add_argument("--verify", action="store_true", help="Run hierarchical verification instead of building JSON")
    parser.add_argument("--tree", action="store_true", help="Print hierarchy outline (used with --verify or alone)")
    parser.add_argument("--track", choices=TRACK_IDS, nargs="+", help="Track filter for --verify")
    parser.add_argument("--unit", help="Major unit filter for --verify (e.g. u1, 3)")
    parser.add_argument("--phase", help="Middle phase filter for --verify (e.g. p14, 14, or substring)")
    parser.add_argument("--week", type=int, help="Specific week filter for --verify")
    parser.add_argument("--strict", action="store_true", help="Treat advisory warnings as failures in --verify")
    args = parser.parse_args(argv)

    if args.verify or args.tree:
        v_argv = []
        if args.tree:
            v_argv.append("--tree")
        if args.track:
            v_argv.extend(["--track", *args.track])
        if args.unit:
            v_argv.extend(["--unit", args.unit])
        if args.phase:
            v_argv.extend(["--phase", args.phase])
        if args.week is not None:
            v_argv.extend(["--week", str(args.week)])
        if args.strict:
            v_argv.append("--strict")
        return verify_main(v_argv)

    tracks = build_all()
    write_roadmap(tracks=tracks)
    return verify_main([])


if __name__ == "__main__":
    sys.exit(main())
