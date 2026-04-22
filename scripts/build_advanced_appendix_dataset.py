"""CLI entrypoint to generate only the advanced valuation and risk appendix."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from copper_risk_model.advanced_appendix import build_advanced_appendix_outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build only the advanced valuation and risk appendix outputs.")
    parser.add_argument(
        "--config-path",
        default="config/project.yaml",
        help="Project configuration used to resolve appendix input modes and defaults.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/bi",
        help="Directory where appendix outputs should be written.",
    )
    parser.add_argument(
        "--input-mode",
        choices=["canonical", "legacy_workbook"],
        default=None,
        help="Appendix input path. Omit to use the repo default from config/project.yaml.",
    )
    parser.add_argument(
        "--benchmark-mode",
        choices=["canonical", "legacy_workbook", "none"],
        default=None,
        help="Benchmark reference path. Omit to use the repo default from config/project.yaml.",
    )
    parser.add_argument(
        "--data-dir",
        default=None,
        help="Override the canonical annual appendix data directory.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    outputs = build_advanced_appendix_outputs(
        config_path=args.config_path,
        output_dir=args.output_dir,
        input_mode=args.input_mode,
        benchmark_mode=args.benchmark_mode,
        data_dir=args.data_dir,
    )
    print("Generated advanced appendix files:")
    for name, path in outputs.items():
        print(f"- {name}: {path}")


if __name__ == "__main__":
    main()
