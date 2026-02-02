# Tech Updates to Slack

Fetches tech updates by topic (Google News RSS), dedupes/summarizes, and posts a daily digest to Slack. Runs at 09:00 UTC via GitHub Actions; can also run manually.

## Setup

1. **Slack**: Create an app, enable Incoming Webhooks, add a webhook to your workspace, copy the webhook URL.
2. **GitHub**: Push this repo. In repo **Settings** → **Secrets and variables** → **Actions**, add secret `SLACK_WEBHOOK_URL` with that URL.
3. **Topics**: Edit `config/sources.yaml` and list topics (e.g. `Python`, `Hacker News`). No URLs—feeds are built from topic names. Optional: `max_items_per_run`, `summary_max_length`, `max_items_per_topic`.

## Run

**Local (dry-run, no Slack):**
```bash
pip install -r requirements.txt
python src/main.py --dry-run
```

**Local (sends to Slack):**
```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK"
python src/main.py
```

**GitHub**: Workflow runs daily at 09:00 UTC. To run now: **Actions** → **Daily tech updates to Slack** → **Run workflow**.
