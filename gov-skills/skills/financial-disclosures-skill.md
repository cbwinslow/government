---
name: financial-disclosures-skill
description: Autonomously parse House and Senate financial disclosure ZIP files (2008-2026), extract stock transactions using OCR/LLMs, map filers to the Master Identity database, and insert transactions as Actions. Use when processing congressional financial disclosures to track stock trades, asset purchases, and conflicts of interest.
category: integration-documentation
risk: medium
source: community
tags: [financial-disclosures, pdf, ocr, llm, congress, stock-trades, identity-resolution, etl]
tools: [python, zipfile, requests, pdfplumber, pymupdf, google-generativeai, sqlalchemy, postgresql]
allowed-tools: Read Write Edit Bash Glob Grep
compatibility: claude-code
---

# Skill: Financial Disclosures Autonomous Processing

**Target Agent:** Extraction/ETL Agent (e.g. Letta, Cline)
**Objective:** Autonomously parse the raw House and Senate financial disclosure ZIP files (2008-2026), extract stock transactions using OCR/LLMs, map the filer to the `opendiscourse` Master Identity database, and insert the transactions as `Actions`.

## Context

The `financial-disclosures/` directory contains roughly 1.3 GB of `.zip` files representing annual financial disclosures for members of Congress. Inside these zips are thousands of raw PDF forms. These forms contain critical information regarding stock trades, asset purchases, and potential conflicts of interest.

Because the PDF layouts change year by year and chamber by chamber, standard python regex/PDF parsers fail. We rely on **you**, the autonomous agent, to coordinate the extraction using LLMs.

## Standard Operating Procedure (SOP)

When instructed to process a specific year (e.g., `Process 2024FD`):

### 1. Data Extraction (The Index Files)
1. Use python's `zipfile` module to extract `financial-disclosures/2024FD.zip`. 
2. **IMPORTANT:** These ZIP files do *not* contain the actual PDFs! They contain index files (`2024FD.txt` and `2024FD.xml`).
3. Parse the index file. It contains columns for `Name`, `Year`, and `DocID`.
4. Construct the PDF download URL using this schema: `https://disclosures-clerk.house.gov/public_disc/financial-pdfs/{Year}/{DocID}.pdf`
5. Download the PDF to a temporary directory `/tmp/fd_pdfs/`.

### 2. OCR and LLM Parsing
For each downloaded PDF:
1. Extract the text. If the PDF is an image scan, use a vision-capable LLM (e.g., `google/gemini-1.5-pro`) to process the document.
2. Send the document text/images to the LLM with the following strict prompt:
   > "You are a financial auditor. Extract all stock transactions (Buy, Sell, Exchange), the asset name (e.g., Apple Inc.), the ticker symbol, the transaction date, and the value range (e.g., $15,001 - $50,000). Output strictly as a JSON array."

### 3. Identity Resolution (CRITICAL)
1. You now have a politician's name (from the index) and a list of transactions.
2. Import the OpenDiscourse database engine:
   ```python
   from opendiscourse.models.database import get_engine, Politician
   from sqlalchemy.orm import Session
   ```
3. Query the `Politician` table to find the matching politician.
   - *Warning: Names can be fuzzy (e.g., "William" vs "Bill"). If a direct match fails, query by last name and verify the state/party.*

### 4. Database Insertion
1. Once the `Politician` entity is found, insert the extracted transactions into the database (you will need to ensure a `Transactions` table or similar JSON field exists on the `Politician` model representing their 'Actions').
2. Commit the transaction. If it fails, log the error and move to the next PDF.
3. Clean up the `/tmp/` directory when finished.

## When to Use
- Processing annual financial disclosure ZIP files (2008-2026)
- Extracting stock transactions from congressional PDF forms
- Mapping disclosure filers to master politician identities
- Building transaction history for Honesty Engine scoring

## Limitations
- ZIP files only contain index files, not actual PDFs (must download separately)
- PDF layouts vary by year and chamber (House vs Senate)
- Requires vision-capable LLM for scanned/image-based PDFs
- Name matching is fuzzy; requires verification by state/party
- Rate limits on disclosure clerk website
- Senate disclosures have different URL structure
