# ⚡ Weaver — Autonomous Self-Healing API Engine

<div align="center">

![Weaver Demo](demo.gif)

[![Built with Hermes](https://img.shields.io/badge/Powered%20by-Hermes--4--405B-blueviolet?style=flat-square&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTIgMkw0IDdWMTdMMTIgMjJMMjAgMTdWN0wxMiAyWiIgZmlsbD0iI2JjOGNmZiIvPjwvc3ZnPg==)](https://nousresearch.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python)](https://python.org)
[![License MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Hackathon](https://img.shields.io/badge/Nous%20Research-Hackathon%202025-ff6b35?style=flat-square)](https://nousresearch.com)

**Point it at any website. Get a live, self-healing REST API. Zero manual code.**

[Live Demo](#-demo) · [Quick Start](#-quick-start) · [Architecture](#️-architecture) · [Telegram Bot](#-telegram-bot)

</div>

---

## The Problem

Web scrapers are fragile. The moment a website renames a CSS class — `.article-card` becomes `.news-item` — your entire data pipeline silently dies. Engineers get paged at 3am to manually inspect new HTML and rewrite selectors.

**This is a solved problem. You just haven't automated the solution yet.**

---

## The Solution

Weaver is a **Hermes Agent Skill** that turns any URL into a monitored, production-ready REST API — and keeps it alive autonomously when the target site changes.

```
You:    "Build an API for https://news.ycombinator.com"

Weaver: 🕵️  Checks robots.txt → allowed
        🌐  Inspects live DOM via browser_tool
        ✍️  Writes FastAPI scraper with correct CSS selectors
        🚀  Deploys on localhost:8000
        👁  Starts health monitor (30s interval)
        ✅  "API live — 30 items at /items"

[Later, the site updates its HTML...]

Weaver: ⚠️  /health returns broken (0 results)
        🔍  DOM fingerprint changed: cards=30 → cards=0|items=30
        ✍️  Rewrites scrape_v2() with new selectors
        💾  Backup saved: backups/scraper_20250310T142233.py.bak
        🔄  Hot-swaps scraper.py — uvicorn reloads
        ✅  "Healed in 14s. Schema v1.0.0 preserved."
```

---

## ⚙️ Architecture

Weaver is built as a true **Hermes Agent Skill** — not a wrapper around an LLM API. The agent uses its own tools to do every step:

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER (Telegram / CLI)                    │
│                  "Build an API for example.com"                 │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │    Hermes Agent     │
                    │  (Hermes-4-405B)    │
                    └──────────┬──────────┘
                               │  reads
                    ┌──────────▼──────────┐
                    │  skills/web/weaver  │
                    │     SKILL.md        │
                    └──────────┬──────────┘
                               │  executes
          ┌────────────────────┼───────────────────────┐
          │                    │                       │
   ┌──────▼──────┐    ┌────────▼────────┐    ┌────────▼────────┐
   │ browser_tool│    │  terminal_tool  │    │   web_extract   │
   │ Browserbase │    │  local / docker │    │   Firecrawl     │
   │             │    │                 │    │                 │
   │ Sees live   │    │ Writes scraper  │    │ robots.txt +    │
   │ rendered DOM│    │ Runs uvicorn    │    │ quick snapshots │
   │ CSS classes │    │ Verifies output │    │                 │
   └──────┬──────┘    └────────┬────────┘    └─────────────────┘
          │                    │
          └────────────────────┘
                    │  produces
          ┌─────────▼──────────────────────────┐
          │         FastAPI Scraper             │
          │                                     │
          │  GET /items    → structured JSON    │
          │  GET /health   → status + DOM FP    │
          │  GET /state    → last scrape meta   │
          │  GET /         → live dashboard     │
          └─────────────────────────────────────┘
                    │  monitored by
          ┌─────────▼──────────────────────────┐
          │      health_check.py --watch 30s    │
          │                                     │
          │  DOM fingerprint diff               │
          │  Auto-trigger self-heal             │
          │  Atomic hot-swap (zero downtime)    │
          │  Backup on every heal               │
          └─────────────────────────────────────┘
```

### Key Design Decisions

| Decision | Why |
|---|---|
| **Real browser inspection** | `browser_tool` sees the actual rendered DOM — not raw HTML guesses |
| **Agent writes the code** | No external LLM API call for generation — Hermes reasons and writes itself |
| **Pydantic schema lock** | Field names never change across heals — downstream consumers stay safe |
| **Atomic hot-swap** | `write to .tmp → rename` — never a half-written file in production |
| **Backup on every heal** | `backups/scraper_{timestamp}.py.bak` — always reversible |

---

## 🚀 Quick Start

### Prerequisites

```bash
# 1. Clone repos
git clone https://github.com/nousresearch/hermes-agent  ~/HERMES/hermes-agent
git clone https://github.com/mehmetkr-31/hermes-apiaas  ~/HERMES/hermes-apiaas

# 2. Install Weaver dependencies
python3 -m venv ~/HERMES/hermes-apiaas/agent/.venv
~/HERMES/hermes-apiaas/agent/.venv/bin/pip install -r ~/HERMES/hermes-apiaas/agent/requirements.txt

# 3. Install Hermes Agent
cd ~/HERMES/hermes-agent
pip install -e ".[messaging]"
```

### Option A — Telegram Bot (Recommended)

The full experience. Chat on Telegram, Weaver does everything.

**Step 1** — Get a bot token from [@BotFather](https://t.me/BotFather)

**Step 2** — Configure `~/.hermes/.env`:

```env
TELEGRAM_BOT_TOKEN=your_token_here
NOUS_API_KEY=your_nous_key_here
GATEWAY_ALLOW_ALL_USERS=true
```

**Step 3** — Install the Weaver skill:

```bash
mkdir -p ~/.hermes/skills/web/weaver
cp ~/HERMES/hermes-apiaas/docs/WEAVER_SKILL.md ~/.hermes/skills/web/weaver/SKILL.md
```

**Step 4** — Start the gateway:

```bash
cd ~/HERMES/hermes-agent
python3 -m hermes_cli.main gateway run
```

**Step 5** — Chat on Telegram:

```
Build an API for https://news.ycombinator.com
```

---

### Option B — Self-Healing Demo (CLI)

Watch the system break and fix itself live:

```bash
cd ~/HERMES/hermes-apiaas

# Set your API key
echo "NOUS_API_KEY=your_key" > .env

# Run the end-to-end demo
./agent/.venv/bin/python demo_heal.py
```

**What you'll see:**
1. Mock university site boots on `:8080`
2. AI-generated API boots on `:8000`
3. CSS classes get renamed (`.announcement-card` → `.ann-item`)
4. API returns `503 Service Unavailable`
5. Health monitor detects the DOM change
6. Hermes rewrites the scraper with new selectors
7. API recovers — **zero data loss, schema unchanged**

---

### Option C — Generate a New API from Scratch (CLI)

```bash
./agent/.venv/bin/python scripts/init_api.py \
    --url "https://news.ycombinator.com" \
    --schema "Post titles, URLs, points, and comment counts"
```

---

## 📡 API Endpoints

Once deployed, your auto-generated API exposes:

| Endpoint | Description | Response |
|---|---|---|
| `GET /` | **Live dashboard** — real-time status, items, heal log | HTML |
| `GET /items` | All scraped items (Pydantic-typed) | JSON |
| `GET /health` | Health check — triggers self-heal if broken | JSON |
| `GET /state` | Last scrape metadata + DOM fingerprint | JSON |
| `GET /docs` | Interactive Swagger UI | HTML |

### Sample Response (`/items`)

```json
{
  "source": "https://news.ycombinator.com",
  "scraped_at": "2025-03-10T14:22:33Z",
  "schema_version": "1.0.0",
  "count": 30,
  "items": [
    {
      "title": "I put my whole life into a single database",
      "category": "HN Story",
      "excerpt": "342 comments",
      "date": "3 hours ago",
      "department": "171 points"
    }
  ]
}
```

### Self-Heal Guarantees

| Guarantee | Detail |
|---|---|
| **Zero data loss** | Last-known-good data served during heal |
| **Schema stability** | `schema_version: "1.0.0"` and all field names locked forever |
| **Atomic hot-swap** | Write to `.tmp` → `rename()` — never a partial file |
| **Backup on every heal** | `agent/backups/scraper_{timestamp}.py.bak` |
| **Telegram alerts** | Break + heal events delivered instantly |
| **Max 3 self-debug cycles** | Escalates to user if still failing |

---

## 🤖 Telegram Bot

The Telegram integration uses the built-in Hermes Gateway — no custom bot code needed.

```
You:   Build an API for https://example.com/news
Bot:   ✅ Weaver API is live!
       📡 http://localhost:8000/items — 24 items
       🏥 http://localhost:8000/health
       👁 Monitoring every 30s

[Site updates HTML 2 hours later]

Bot:   ⚠️ API broken — 503 on /items
       🔧 DOM fingerprint changed
       ✅ Healed in 18s. Schema v1.0.0 preserved.
```

Available commands in chat:

| Message | What happens |
|---|---|
| `Build an API for <url>` | Generates and deploys a new scraper |
| `Heal the API` | Manually triggers self-heal |
| `Check API status` | Returns current health + item count |
| `Stop monitoring` | Stops the health monitor |

---

## 🗂️ Project Structure

```
hermes-apiaas/
├── agent/
│   ├── scraper.py              # Live FastAPI app (auto-generated + healed)
│   ├── scraper_v1.py           # Demo baseline (original selectors)
│   ├── scraper_v2.py           # Demo healed (post-DOM-change selectors)
│   ├── dashboard.py            # Real-time web dashboard (GET /)
│   ├── backups/                # Timestamped scraper backups
│   ├── state.json              # Last successful scrape state
│   └── requirements.txt
│
├── scripts/
│   ├── init_api.py             # Zero-to-One generator (LLM API mode)
│   └── health_check.py         # Self-healing orchestrator
│
├── mock-site/
│   ├── index_working.html      # Original DOM (6 announcements)
│   ├── index_broken.html       # Broken DOM (CSS classes renamed)
│   └── server.py               # Local HTTP server for demo
│
├── docs/
│   └── WEAVER_SKILL.md         # Hermes Agent skill definition (v2)
│
├── demo_heal.py                # End-to-end self-healing demo
├── docker-compose.yml          # Docker deployment (3 services)
└── README.md
```

---

## 🐳 Docker Deployment

```bash
# Copy your API key
cp .env.example .env
echo "NOUS_API_KEY=your_key" >> .env

# Start all 3 services
docker compose up

# Services:
#   :8080  →  Mock university website
#   :8000  →  Auto-generated FastAPI scraper
#   health-monitor  →  Self-healing orchestrator (30s interval)
```

---

## 🔑 Environment Variables

### `hermes-agent` (`~/.hermes/.env`)

| Variable | Required | Description |
|---|---|---|
| `NOUS_API_KEY` | ✅ | Nous Research inference API |
| `TELEGRAM_BOT_TOKEN` | Telegram | From @BotFather |
| `TELEGRAM_ALLOWED_USERS` | Recommended | Your Telegram user ID |
| `BROWSERBASE_API_KEY` | browser_tool | Cloud browser for DOM inspection |
| `FIRECRAWL_API_KEY` | web_extract | Fast static page extraction |

### `hermes-apiaas` (`.env`)

| Variable | Required | Description |
|---|---|---|
| `NOUS_API_KEY` | ✅ | For `init_api.py` and `health_check.py` |
| `API_BASE` | No | FastAPI URL (default: `http://localhost:8000`) |
| `TARGET_URL` | No | Target site (default: `http://localhost:8080`) |

---

## 🎬 Demo

Watch Weaver detect a broken site and autonomously heal itself in real time:

![Weaver Self-Healing Demo](demo.gif)

**Demo flow (30 seconds):**
1. API serving 6 announcements from mock university site ✅
2. CSS classes renamed on target site — API returns `503` ❌
3. Weaver detects DOM change, rewrites selectors, hot-swaps code
4. API restored — same schema, same field names, zero downtime ✅

---

## 🏗️ Built With

| Technology | Role |
|---|---|
| [Hermes-4-405B](https://nousresearch.com) | LLM backbone — reasoning, code generation |
| [Hermes Agent](https://github.com/nousresearch/hermes-agent) | Agent framework — browser, terminal, web tools |
| [FastAPI](https://fastapi.tiangolo.com) | Generated API framework |
| [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) | HTML parsing + CSS selector extraction |
| [Browserbase](https://browserbase.com) | Cloud browser for live DOM inspection |
| [Firecrawl](https://firecrawl.dev) | Fast static page extraction |
| [python-telegram-bot](https://python-telegram-bot.org) | Telegram gateway |
| [uvicorn](https://www.uvicorn.org) | ASGI server with hot-reload support |

---

## 🤝 Hackathon Notes

This project was built for the **Nous Research Hackathon 2025** and demonstrates two complementary integration patterns:

1. **Hermes Agent Skill** (`skills/web/weaver/SKILL.md`) — The canonical implementation. The agent uses `browser_tool`, `terminal_tool`, and `web_extract` to inspect, generate, deploy, and heal scrapers autonomously. No hardcoded selectors, no external code generation API.

2. **Standalone scripts** (`scripts/init_api.py`, `scripts/health_check.py`) — For environments without the full agent stack, these call Hermes-4-405B inference API directly. Useful for CI/CD or minimal deployments.

Both approaches share the same FastAPI structure, Pydantic schemas, and self-healing guarantees.

---

<div align="center">

Made with ⚡ by [mehmetkr-31](https://github.com/mehmetkr-31) · Powered by [Nous Research](https://nousresearch.com)

</div>