# OpenDiscourse: The Honesty Engine

**OpenDiscourse** is an open-source political intelligence database designed to scale public interest research. It cross-references what politicians vote on against their speeches, social media, and campaign finance data to identify discrepancies and build a comprehensive "Consistency Score."

Built with scalability and reproducibility in mind, this project allows researchers, journalists, and citizens to host their own intelligence nodes and track their local or federal governments.

## 🌟 Features

- **Master Identity Resolution:** A unified PostgreSQL database linking politicians across disparate datasets (OpenStates, Congress, FEC).
- **The "Actions" Pipeline:** Automated scrapers pulling from OpenSecrets (Campaign Finance) and Project Vote Smart (Interest Group Ratings).
- **The "Words" Pipeline:** Ingests global news mentions via GDELT, and official floor speeches via Congress.gov.
- **The LLM Honesty Scorer:** Utilizes OpenRouter and Gemini Pro to analyze the delta between a politician's stated positions and actual votes.

## 🚀 Quick Start (For Researchers & Developers)

We built this to be reproducible. You can run your own instance of OpenDiscourse in minutes.

### 1. Prerequisites

- [uv](https://github.com/astral-sh/uv) (for lightning-fast Python package management)
- Docker & Docker Compose (for PostgreSQL and Qdrant)

### 2. Infrastructure Setup

Spin up the required databases (PostgreSQL with pgvector, Qdrant, and Redis):

```bash
docker-compose up -d
```

### 3. Environment Configuration

Copy the template and add your API keys:

```bash
cp .env.example .env
```

*Note: The application is modular. If you don't have an API key for a specific service (like OpenSecrets), that specific scraper will simply be bypassed.*

### 4. Installation

Install the package using `uv`:

```bash
uv sync
```

## 🏗️ Architecture Overview

The codebase follows strict Python industry standards to ensure it is portable and easy to extend:

- `src/opendiscourse/core/` - Pydantic settings and configuration manager.
- `src/opendiscourse/models/` - SQLAlchemy schemas for the relational database.
- `src/opendiscourse/ingestion/` - Modular adapters for pulling data (GDELT, OpenSecrets, etc.).
- `src/opendiscourse/engine/` - The LLM logic for running Consistency Scoring.
- `src/opendiscourse/api/` - The FastAPI backend serving the dashboard.

## 🤝 Contributing

This project is built for the community. If you have a new data source you'd like to integrate, simply add a new module to `src/opendiscourse/ingestion/` and submit a Pull Request!
