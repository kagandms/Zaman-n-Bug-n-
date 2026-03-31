# Tarihte Bugun Botu

Production-oriented Python bot that turns "On This Day" events into Turkish X threads, enriches them with AI-generated copy, attaches an image, and posts them as a thread.

![Sample output 1](docs/assets/bot-sample-output-1.png)
![Sample output 2](docs/assets/bot-sample-output-2.png)

## What It Does

- fetches events from the Turkish Wikipedia `onthisday` feed
- prioritizes Turkey-related events before falling back to other notable items
- rewrites selected events into a short X thread via OpenRouter
- downloads a Wikipedia image when available, otherwise generates a fallback image URL
- posts the thread to X and stores posted content in a local database to reduce repeats

## Stack

- Python 3.11
- `httpx` for async HTTP calls
- `tweepy` for X API integration
- `SQLAlchemy` + `aiosqlite` for async persistence
- `pydantic-settings` for configuration
- GitHub Actions for scheduled execution

## Project Layout

```text
src/
  core/        configuration and logging
  data/        SQLAlchemy models and repository layer
  services/    content, AI, image, and X integration
  utils/       text processing helpers
tests/         unit tests
archive/       deprecated pre-v4 reference scripts
docs/assets/   README screenshots
```

## Quick Start

1. Create a virtual environment and install dependencies.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Create your local environment file.

```bash
cp .env.example .env
```

3. Run the bot in safe mode first.

```bash
python -m src.main
```

Set `DRY_RUN=true` in `.env` while validating the end-to-end flow. Switch it to `false` only after credentials and posting behavior are confirmed.

## Required Environment Variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `API_KEY` | yes | X consumer key |
| `API_SECRET` | yes | X consumer secret |
| `ACCESS_TOKEN` | yes | X access token |
| `ACCESS_TOKEN_SECRET` | yes | X access token secret |
| `OPENROUTER_API_KEY` | yes | OpenRouter API key |
| `BEARER_TOKEN` | no | optional X v2 bearer token |
| `DATABASE_URL` | no | defaults to local SQLite |
| `DRY_RUN` | no | disables posting when `true` |

## GitHub Actions

The scheduled workflow lives at `.github/workflows/daily-bot.yml`.

Required repository secrets:

- `API_KEY`
- `API_SECRET`
- `ACCESS_TOKEN`
- `ACCESS_TOKEN_SECRET`
- `OPENROUTER_API_KEY`

## Operational Notes

- Runtime state is no longer committed back into git. This repository is now source-only.
- Local default persistence uses `sqlite+aiosqlite:///bot_data.db`.
- If you need cross-run duplicate protection in GitHub Actions, move `DATABASE_URL` to a persistent external database and add the corresponding async driver dependency.
- Logs are written to `logs/bot.log` locally.

## Tests

```bash
pytest -q
```

## Entry Points

- Supported runtime: `python -m src.main`
- Legacy reference scripts: `archive/`
