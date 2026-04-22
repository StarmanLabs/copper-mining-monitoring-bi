"""CLI entrypoint to generate the monthly refresh support package."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from copper_risk_model.monthly_monitoring import build_monthly_monitoring_outputs
from copper_risk_model.refresh_reporting import build_failed_refresh_summary


def _default_mapping_config() -> Path:
    return Path("config") / "mappings" / "public_demo_identity_mapping.yaml"


def _public_safe_arg(path: str) -> str:
    candidate = Path(path)
    if not candidate.is_absolute():
        return candidate.as_posix()
    try:
        return candidate.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return candidate.name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the public-safe monthly refresh package.")
    parser.add_argument(
        "--data-dir",
        default="data/sample_data/monthly_monitoring",
        help="Directory containing the raw monthly source exports to map.",
    )
    parser.add_argument(
        "--mapping-config",
        default=str(_default_mapping_config()),
        help="YAML mapping config used to convert source exports into canonical monthly schemas.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/bi",
        help="Directory where refresh outputs should be written.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        outputs = build_monthly_monitoring_outputs(
            data_dir=args.data_dir,
            mapping_config_path=args.mapping_config,
            output_dir=output_dir,
        )
    except Exception as error:
        failure_summary = build_failed_refresh_summary(
            error=error,
            mapping_config_path=_public_safe_arg(args.mapping_config),
            data_dir=_public_safe_arg(args.data_dir),
        )
        failure_path = output_dir / "refresh_summary.json"
        failure_path.write_text(json.dumps(failure_summary, indent=2), encoding="utf-8")
        raise

    print("Generated refresh package files:")
    for name, path in outputs.items():
        print(f"- {name}: {path}")


if __name__ == "__main__":
    main()
