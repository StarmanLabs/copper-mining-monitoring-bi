"""CLI entrypoint to generate BI-ready datasets."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from copper_risk_model.bi_export import build_bi_outputs
from copper_risk_model.powerbi_native_scaffold import build_powerbi_native_scaffold
from copper_risk_model.powerbi_template import build_powerbi_template_layer


def main() -> None:
    outputs = build_bi_outputs()
    template_outputs = build_powerbi_template_layer()
    native_scaffold_outputs = build_powerbi_native_scaffold()
    print("Generated files:")
    for name, path in outputs.items():
        print(f"- {name}: {path}")
    print("Generated Power BI template files:")
    for name, path in template_outputs.items():
        print(f"- {name}: {path}")
    print("Generated PBIP/TMDL-oriented scaffold files:")
    for name, path in native_scaffold_outputs.items():
        print(f"- {name}: {path}")


if __name__ == "__main__":
    main()
