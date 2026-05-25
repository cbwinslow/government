# Skill: campaign-finance-ingestion-admin

## Purpose
Use this skill for FEC/OpenFEC campaign finance ingestion and normalization, including candidates, committees, contributions, disbursements, filings, schedules, independent expenditures, and committee-candidate relationships.

## Source facts to honor
- OpenFEC is a RESTful API for FEC data.
- FEC provides searchable and historical campaign finance data.
- Individual contributor information is subject to legal restrictions on sale or solicitation use.

## Recommended pipeline
1. Pull candidate and committee registries.
2. Pull candidate-committee histories and cycle summaries.
3. Pull schedules/itemized contributions and disbursements as needed.
4. Pull filings and filing metadata.
5. Normalize to committee, candidate, contributor, payee, transaction, and filing tables.
6. Link all candidate/committee records back to canonical `master.person` and `master.organization`.

## Core tables
- `finance.candidate`
- `finance.committee`
- `finance.candidate_committee_link`
- `finance.filing`
- `finance.contribution`
- `finance.expenditure`
- `finance.independent_expenditure`
- `finance.committee_cycle_summary`
- `finance.contributor`
- `finance.payee`

## Admin concerns
- partition large transaction tables by two-year cycle.
- maintain source IDs and filing document links.
- preserve amendment lineage on filings.
- validate cycle rollups against FEC summaries.
