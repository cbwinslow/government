# OpenDiscourse Configuration

## Precedence

Configuration is resolved in this order, with later layers taking precedence:

1. typed application defaults;
2. `config/default.toml` or another explicitly selected TOML file;
3. `.env` for local development;
4. process environment variables;
5. explicit CLI overrides when implemented.

Environment variables use the `OPENDISCOURSE_` prefix and double underscores for nested settings.

```text
OPENDISCOURSE_DATABASE__DSN
OPENDISCOURSE_STORAGE__ROOT
OPENDISCOURSE_STORAGE__TEMP_ROOT
OPENDISCOURSE_HTTP__TIMEOUT_SECONDS
OPENDISCOURSE_SOURCES__GOVINFO_API_KEY
```

## Secrets

Real credentials belong in environment variables or a secret manager. Commit `.env.example`, never `.env`. Configuration display commands must redact secrets.

## Commands

```bash
cp .env.example .env
python -m pip install -e '.[dev]'
opendiscourse config show
opendiscourse doctor
opendiscourse fixture sync
```

`config show` prints a validated, redacted representation. `doctor` initializes and verifies the configured local storage directories.

## Production guidance

- Replace the development database credentials.
- Mount configuration and secrets rather than baking them into images.
- Use a dedicated PostgreSQL role with least privilege.
- Put the data lake on durable storage with backups and integrity checks.
- Set a descriptive HTTP user agent and source-specific concurrency limits.
