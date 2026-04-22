# Getting Started

This repository supports two honest usage paths:

1. public portfolio review
2. local private adaptation

Use the public path first unless you already have governed company exports and local mappings ready.

## Path 1: Public Portfolio Review

Use this path when you want to understand the project, review the outputs, or continue the public-safe Power BI baseline.

What you need:

- Python 3.12 or another compatible local Python environment
- the repository checked out locally
- no private company data

Recommended sequence:

1. install dependencies
   `python -m pip install -e .[dev]`
2. build the public-safe baseline
   `python scripts/build_bi_dataset.py`
3. review the main outputs under `outputs/bi/`
4. read `powerbi/START_HERE.md`
5. continue in Power BI Desktop from `powerbi/pbip_tmdl_scaffold/`

What this gives you:

- monthly actual-vs-plan marts
- data-quality and refresh-support outputs
- annual appendix and advanced appendix outputs
- Power BI starter catalogs
- template and PBIP/TMDL-oriented continuation scaffolds

## Path 2: Local Private Adaptation

Use this path when you want to keep the public repository structure but point the workflows to local private exports and local mappings.

What you need:

- governed local source exports
- a local source profile copied from the template
- local mapping files copied from the mapping templates
- ignored local folders for private raw data and private outputs

Recommended sequence:

1. copy `config/source_profiles/templates/example_private_company_profile.yaml`
2. save it as something like `config/source_profiles/local/my_company_profile.yaml`
3. copy the mapping templates you need into `config/mappings/local/`
4. point the profile to your local raw source folders, mappings, and output folders
5. prevalidate the profile
   `python scripts/run_local_profile.py --profile config/source_profiles/local/my_company_profile.yaml --validate-only`
6. run the monthly path first
   `python scripts/run_local_profile.py --profile config/source_profiles/local/my_company_profile.yaml --scope monthly`
7. run the appendix path only if you really need it
   `python scripts/run_local_profile.py --profile config/source_profiles/local/my_company_profile.yaml --scope all`
8. rebuild the Power BI scaffold with the same profile
   `python scripts/build_powerbi_native_scaffold.py --profile config/source_profiles/local/my_company_profile.yaml`

What to keep out of version control:

- private raw files under `data/private/`
- local source profiles under `config/source_profiles/local/`
- local mappings under `config/mappings/local/`
- private Power BI Desktop files

## Practical Rule

Keep the project monthly-first.

Start with the monthly monitoring path, shared dimensions, and management-control pages.

Treat the annual and advanced appendix layers as secondary continuation logic, not as the opening story of the repository.
