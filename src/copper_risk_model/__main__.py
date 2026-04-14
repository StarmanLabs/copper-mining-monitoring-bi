"""Module entrypoint."""

from .bi_export import build_bi_outputs
from .dashboard_builder import build_portfolio_dashboard


def main() -> None:
    build_bi_outputs()
    build_portfolio_dashboard()


if __name__ == "__main__":
    main()
