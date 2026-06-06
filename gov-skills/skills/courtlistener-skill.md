# Skill: Courtlistener Legal History Extraction

**Target Agent:** Research/ETL Agent
**Objective:** Autonomously query the Courtlistener RECAP API to find lawsuits, dockets, and legal opinions involving politicians, extract the core conflict, and append it to the `opendiscourse` database as an 'Action' or 'Discrepancy'.

## Context

Politicians are frequently involved in lawsuits—either as plaintiffs, defendants, or amici curiae. These legal actions are often more indicative of their true ideological stances than their public speeches. Courtlistener is the premier open-source database for US federal and state court records.

## Standard Operating Procedure (SOP)

When instructed to audit a specific politician or process a batch of politicians:

### 1. Identify Target
1. Connect to the `opendiscourse` Postgres database.
2. Retrieve the politician's full legal name, state, and roles.

### 2. Query Courtlistener
1. Use the `httpx` library to hit the Courtlistener Search API: `https://www.courtlistener.com/api/rest/v3/search/`.
2. **CRITICAL:** The Courtlistener API blocks anonymous requests. You must include your API key in the headers:
   `Authorization: Token <YOUR_COURTLISTENER_TOKEN>`
   *(Retrieve this from `settings.COURTLISTENER_API_KEY`)*
3. Construct a precise query. Example: `q="John Doe" AND (type:opinion OR type:docket)`.
4. Filter out obvious false positives (e.g., if the politician is from New York, prioritize 2nd Circuit or NY state courts).

### 3. Summarize the Legal Conflict
1. For each highly relevant docket/opinion retrieved, extract the case summary or the raw opinion text.
2. Pass the text to an LLM (via OpenRouter/Gemini) with the prompt:
   > "You are a legal analyst. Summarize this court case in 2 paragraphs. Identify what the politician's legal stance was (e.g., suing to block an environmental regulation). Classify this stance into a political issue category."

### 4. Update the Database
1. Map the summarized legal stance to the politician's record in the `opendiscourse` database.
2. This data should be classified under the 'Actions' array for the Honesty Engine to evaluate later.
