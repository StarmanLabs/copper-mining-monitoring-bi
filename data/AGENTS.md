# AGENTS.md

## Scope

This file applies to everything under `data/`.

## Purpose of data folder

The `data/` tree should reflect a clean analytical pipeline.

Preferred layers:
- raw
- staging
- curated
- marts
- sample_data or examples where useful

## Rules for datasets

Every new dataset should have:
- clear grain
- explicit units
- stable key logic
- readable column naming
- documented assumptions

## Sample data rules

Sample datasets are allowed and encouraged for portfolio demonstration.
However:
- do not present sample data as live mine data
- do not imply ERP or plant integration where none exists
- make sample datasets realistic enough to support planning/control demos

## Column conventions

Prefer:
- snake_case
- explicit units or metric meaning when useful
- `period` or `month` fields with consistent format
- scenario IDs only when scenario logic is relevant

## Avoid

- ambiguous date formats
- mixed units in the same column
- undocumented derived fields
- random synthetic columns with no dashboard purpose
