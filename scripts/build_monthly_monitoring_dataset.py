"""CLI entrypoint to generate the monthly monitoring layer without the workbook."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from copper_risk_model.monthly_monitoring import build_monthly_monitoring_outputs


def main() -> None:
    outputs = build_monthly_monitoring_outputs()
    print("Generated monthly monitoring files:")
    for name, path in outputs.items():
        print(f"- {name}: {path}")


if __name__ == "__main__":
    main()
