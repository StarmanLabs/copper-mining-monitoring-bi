"""Build BI exports and the self-contained portfolio dashboard."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from copper_risk_model.bi_export import build_bi_outputs
from copper_risk_model.dashboard_builder import build_portfolio_dashboard


def main() -> None:
    bi_outputs = build_bi_outputs()
    dashboard_outputs = build_portfolio_dashboard()

    print("Generated BI files:")
    for name, path in bi_outputs.items():
        print(f"- {name}: {path}")

    print("\nGenerated dashboard files:")
    for name, path in dashboard_outputs.items():
        print(f"- {name}: {path}")


if __name__ == "__main__":
    main()
