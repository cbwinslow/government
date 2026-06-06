# Playbook: OpenDiscourse Database Population Agent

**Target Agent:** All Agents interacting with the `opendiscourse` project.
**Objective:** Ensure strict, conflict-free interaction with the central PostgreSQL database when inserting newly discovered politicians, words, or actions.

## Core Directives

The `opendiscourse` project relies on a central "Master Identity" table (`Politician`) to map disparate IDs across the federal and state governments. **Never** insert duplicate politicians.

### Database Connection Standard
Always use the centralized settings manager to connect to the database. Never hardcode credentials.
```python
from opendiscourse.core.config import settings
from opendiscourse.models.database import get_engine, Politician
from sqlalchemy.orm import Session

engine = get_engine()
session = Session(engine)
```

### Entity Resolution Protocol (How to Search)
When you discover a new piece of data (e.g., a news article from GDELT, a stock trade from Financial Disclosures), you must map it to the correct politician. Follow this hierarchy of resolution:

1. **Exact ID Match (Fastest & Safest):**
   If the source data provides a Bioguide ID, FEC ID, OpenSecrets ID, or OpenStates ID, query the database directly:
   `session.query(Politician).filter(Politician.bioguide_id == "N000194").first()`

2. **Full Name & State Match:**
   If no ID is available, query by `first_name`, `last_name`, and `state`.
   *Beware: First names often vary (e.g., "Robert" vs "Bob"). Use SQLAlchemy `ilike` for fuzzy matching.*

3. **Creation (Last Resort):**
   If and ONLY IF you have exhausted ID and Name searches, you may create a new `Politician` record.

### Inserting 'Words' and 'Actions'
The core of the Honesty Engine relies on Words (what they say) and Actions (what they do).
When you find a new quote or a new vote:
1. Ensure a relational table exists for the data (e.g., `Quotes` or `Votes` with a ForeignKey linking to `Politician.id`). If it doesn't exist, create the SQLAlchemy model in `src/opendiscourse/models/database.py` and run a migration or `Base.metadata.create_all()`.
2. Insert the record.
3. Call `session.commit()`.

### Handling Exceptions
If a database constraint fails (e.g., `IntegrityError` due to a duplicate unique ID):
1. Catch the exception.
2. Call `session.rollback()`.
3. Log the error and proceed to the next item. Do not crash the entire ingestion swarm.
