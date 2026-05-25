# Skill: financial-disclosure-ingestion-admin

## Purpose
Use this skill for congressional financial disclosure, PTR, asset, liability, income, gift, reimbursement, travel, and transaction ingestion.

## Source facts to honor
- House FD reports and PTRs may be filed through https://fd.house.gov and are filed with the Clerk.
- House public disclosure materials are available through the Clerk disclosure system.
- PTRs are required for certain financial transactions such as buying or selling stock, and absent extension are due within 45 days after the transaction.
- Senate and House disclosures can differ in formats and workflows, so keep pipelines source-specific.

## Recommended pipeline
1. Discover filer lists and filing indexes.
2. Download annual disclosures, amendments, and PTRs.
3. Preserve PDFs/HTML/XML and extracted text.
4. Parse holdings, liabilities, income, transactions, gifts, travel, and agreements into normalized tables.
5. Link issuers and assets to canonical organization/security dimensions when possible.
6. Compute transaction timelines and conflict-of-interest heuristics.

## Core tables
- `disclosure.filer`
- `disclosure.report`
- `disclosure.ptr_report`
- `disclosure.asset_holding`
- `disclosure.liability`
- `disclosure.earned_income`
- `disclosure.unearned_income`
- `disclosure.gift`
- `disclosure.travel`
- `disclosure.transaction`
- `disclosure.filing_asset_reference`

## Parsing guidance
- keep source images/PDFs and extracted text.
- preserve original value ranges when exact amounts are undisclosed.
- model transaction type, owner, asset name, ticker, filing date, transaction date, amount range, and comments.
- maintain parser provenance and confidence flags.
