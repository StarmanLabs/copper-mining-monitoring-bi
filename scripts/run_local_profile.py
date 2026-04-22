"""CLI entrypoint for the profile-driven local execution flow."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from copper_risk_model.local_profile_runner import (  # noqa: E402
    RUNNER_SCOPE_CHOICES,
    RUNNER_SUCCESS_STATUSES,
    render_local_profile_console_summary,
    run_local_source_profile,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the local monthly and annual work packages from a single source profile."
    )
    parser.add_argument(
        "--profile",
        required=True,
        help="YAML source profile that defines local inputs, mappings, outputs, and appendix continuation behavior.",
    )
    parser.add_argument(
        "--scope",
        choices=RUNNER_SCOPE_CHOICES,
        default=None,
        help="Override the profile default scope. Choose monthly, annual_appendix, or all.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the planned execution and preflight results without running any package.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate the profile contract, mappings, and expected inputs without building outputs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run_local_source_profile(
        args.profile,
        scope=args.scope,
        dry_run=args.dry_run,
        validate_only=args.validate_only,
    )
    print(render_local_profile_console_summary(summary))
    if summary["runner_status"] not in RUNNER_SUCCESS_STATUSES:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
