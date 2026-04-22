# Private Deployment Pattern

This document defines the intended public/private operating pattern for the repository.

The objective is simple:

- keep the public repo clean and recruiter-readable
- make local/private adaptation practical for real mining analytics work

## What Belongs In The Public Repo

Public-safe content belongs here:

- source-agnostic code
- canonical schemas
- mapping templates
- source-profile templates
- sample/demo inputs
- BI starter kit assets
- public-safe generated marts and catalogs
- documentation

## What Belongs Only In Local/Private Usage

Local/private content belongs outside Git or in ignored local folders only:

- company raw exports
- organization-specific mapping files
- private source profiles
- local dashboard binaries
- local benchmark tables
- scenario decks tied to confidential planning assumptions
- handoff files prepared for internal users

## What Should Never Be Committed

Do not commit:

- `data/private/`
- `config/source_profiles/local/`
- `config/mappings/local/`
- `outputs/private/`
- `powerbi/local/`
- `*.pbix`
- `*.pbit`
- `*.twb`
- `*.twbx`

## Recommended Local Folder Pattern

Use a local structure like this:

```text
data/private/
  monthly_exports/
  annual_appendix_exports/

config/source_profiles/local/
  my_company_profile.yaml

config/mappings/local/
  monthly_private_mapping.yaml
  annual_appendix_private_mapping.yaml

outputs/private/
  monthly_work_core/
  annual_appendix_canonical/
  annual_appendix_report/

powerbi/local/
  my_company_monitoring.pbix
```

That pattern keeps raw private content, canonical local outputs, and local dashboard files clearly separated.

## Recommended Operating Boundary

Treat the repository in three layers:

1. raw private sources
   never committed
2. canonical local outputs
   reusable, local-first, usually still private
3. public-safe code and documented schemas
   committed

The canonical local outputs are the handoff boundary.

That means:

- monthly raw exports should be mapped into canonical monthly datasets
- annual private appendix exports should be mapped into canonical annual appendix datasets
- Power BI should point to canonical outputs, not to raw private exports

## Local Run Pattern

Preferred unified runner:

```bash
python scripts/run_local_profile.py --profile config/source_profiles/local/my_company_profile.yaml --scope all
```

Monthly monitoring only:

```bash
python scripts/run_local_profile.py --profile config/source_profiles/local/my_company_profile.yaml --scope monthly
```

Annual appendix continuation only:

```bash
python scripts/run_local_profile.py --profile config/source_profiles/local/my_company_profile.yaml --scope annual_appendix
```

Low-level monthly monitoring entrypoint:

```bash
python scripts/build_refresh_package.py --data-dir data/private/monthly_exports --mapping-config config/mappings/local/monthly_private_mapping.yaml --output-dir outputs/private/monthly_work_core
```

Low-level annual appendix canonicalization:

```bash
python scripts/build_annual_appendix_work_package.py --data-dir data/private/annual_appendix_exports --mapping-config config/mappings/local/annual_appendix_private_mapping.yaml --output-dir outputs/private/annual_appendix_canonical
```

Appendix report build from local canonical annual outputs:

```bash
python scripts/build_advanced_appendix_dataset.py --data-dir outputs/private/annual_appendix_canonical --benchmark-mode canonical --output-dir outputs/private/annual_appendix_report
```

## Source Profiles

Use source profiles only as local coordination files.

The public-safe template is:

- `config/source_profiles/templates/example_private_company_profile.yaml`

Copy it into:

- `config/source_profiles/local/`

and edit it there.

The template exists to make local work repeatable, not to push private configuration into the public repo.

## Local Dashboard Guidance

Keep local dashboard files under:

- `powerbi/local/`

or outside the repo entirely.

The public repo should keep:

- Power BI starter-kit docs
- query scaffolds
- PBIP/TMDL-oriented scaffolds

The public repo should not become a container for company-specific `.pbix` work.

## Why This Pattern Matters

This pattern improves real-work usability because it lets the repository function as:

- a public analytical portfolio
- a local reusable mining analytics core

without mixing those two responsibilities in one unsafe folder structure.
