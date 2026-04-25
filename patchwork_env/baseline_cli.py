"""CLI sub-commands for baseline capture and drift detection."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from patchwork_env.env_baseline import Baseline, capture_baseline, detect_drift
from patchwork_env.snapshot import capture
from patchwork_env.baseline_formatter import format_drift_report, format_drift_summary


def _load_baseline(path: str) -> Baseline:
    data = json.loads(Path(path).read_text())
    return Baseline.from_dict(data)


def _save_baseline(baseline: Baseline, path: str) -> None:
    Path(path).write_text(json.dumps(baseline.to_dict(), indent=2))


def register_baseline_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("baseline", help="Capture or diff a baseline .env state")
    sub = p.add_subparsers(dest="baseline_cmd", required=True)

    cap = sub.add_parser("capture", help="Capture current .env as a named baseline")
    cap.add_argument("env_file", help="Path to .env file")
    cap.add_argument("--name", required=True, help="Baseline name")
    cap.add_argument("--output", required=True, help="Output JSON path")

    drift = sub.add_parser("drift", help="Detect drift vs a saved baseline")
    drift.add_argument("baseline_file", help="Path to baseline JSON")
    drift.add_argument("env_file", help="Current .env file to compare")
    drift.add_argument("--fail-on-drift", action="store_true", default=False)


def cmd_baseline(args: argparse.Namespace) -> int:
    if args.baseline_cmd == "capture":
        snap = capture(args.env_file)
        baseline = capture_baseline(snap, name=args.name)
        _save_baseline(baseline, args.output)
        print(f"Baseline '{args.name}' saved to {args.output} ({len(baseline.entries)} entries).")
        return 0

    if args.baseline_cmd == "drift":
        baseline = _load_baseline(args.baseline_file)
        snap = capture(args.env_file)
        drifts = detect_drift(baseline, snap)
        print(format_drift_report(drifts, baseline.name, snap.filename))
        print()
        print(format_drift_summary(drifts))
        if args.fail_on_drift and drifts:
            return 1
        return 0

    print(f"Unknown baseline sub-command: {args.baseline_cmd}", file=sys.stderr)
    return 2
