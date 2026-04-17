# Skill: repo-hardening-qa

## Scope

This is a repository-local skill for `copper_minning_risk_model`.

Use it only for this project and for hardening work that improves reliability, reproducibility, structural quality, and documentation alignment across the current repository.

## Current repository context

This repository already includes:

- analytical tests
- build scripts for BI outputs
- a dashboard build script
- advanced analytical modules
- documentation that must stay aligned with the current planning/control/BI positioning

This skill should validate and strengthen those pieces in the context of this repository specifically. It should not be treated as a generic QA template.

## Purpose

Strengthen reliability, test coverage, reproducibility, and structural quality across the repository.

## When to use

Use this skill when the task involves:
- after refactors
- before merging large branches
- validation gaps
- test gaps
- deprecated APIs
- brittle scripts
- docs drift

## QA priorities

1. test meaningful business logic
2. verify CLI scripts still run
3. catch broken assumptions
4. detect naming inconsistencies
5. ensure docs reflect current reality

## Mandatory checks mindset

Check:
- tests
- build scripts
- outputs where relevant
- schema assumptions
- docs alignment
- deprecated or risky code paths

## Preferred fixes

Prefer small, high-value hardening:
- schema tests
- smoke tests
- transformation tests
- explicit failure messages
- reproducibility improvements

## Avoid

Avoid:
- test theater
- huge refactors disguised as QA
- overcomplicated CI plans if simple local checks solve the issue

## Completion checklist

Before finishing:
- list what was checked
- list what still remains fragile
- state whether failures are real blockers or known limitations
- confirm the QA pass reflects the current reality of this repository rather than a generic checklist
