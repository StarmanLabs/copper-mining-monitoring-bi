"""CLI entrypoint to regenerate the public-safe Power BI template layer."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from copper_risk_model.bi_export import build_bi_outputs
from copper_risk_model.powerbi_template import build_powerbi_template_layer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Regenerate the public-safe Power BI Desktop finalization package.")
    parser.add_argument(
        "--profile",
        default=None,
        help="Optional local source profile used only to parameterize monthly and appendix output roots in the scaffold.",
    )
    parser.add_argument(
        "--bi-output-dir",
        default="outputs/bi",
        help="Directory containing the public-safe BI catalogs used to build the scaffold.",
    )
    parser.add_argument(
        "--template-dir",
        default=None,
        help="Override the target template scaffold directory.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_bi_outputs(output_dir=args.bi_output_dir)
    outputs = build_powerbi_template_layer(
        bi_output_dir=args.bi_output_dir,
        template_dir=args.template_dir or ROOT / "powerbi" / "template_scaffold",
        profile_path=args.profile,
    )
    print("Generated Power BI template files:")
    for name, path in outputs.items():
        print(f"- {name}: {path}")


if __name__ == "__main__":
    main()
