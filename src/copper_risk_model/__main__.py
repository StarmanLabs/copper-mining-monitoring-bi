"""Module entrypoint."""

from .bi_export import build_bi_outputs
from .powerbi_native_scaffold import build_powerbi_native_scaffold
from .powerbi_template import build_powerbi_template_layer


def main() -> None:
    build_bi_outputs()
    build_powerbi_template_layer()
    build_powerbi_native_scaffold()


if __name__ == "__main__":
    main()
