# 🎬 Weaver Demo Script — Hackathon Video

**Total runtime:** ~90 seconds  
**Format:** Screen recording + voiceover  
**Tools needed:** Terminal, Browser, Telegram

---

## Pre-Recording Checklist

```bash
# 1. Reset environment
cd ~/HERMES/hermes-apiaas
cp agent/scraper_v1.py agent/scraper.py
rm -f agent/state.json agent/heal_log.jsonl
rm -f agent/backups/*

# 2. Start mock site
python3 mock-site/server.py &

# 3. Start API
cd agent && .venv/bin/uvicorn scraper:app --host 0.0.0.0 --port 8000 &

# 4. Open browser tabs (pre-load, do NOT show yet)
#    Tab 1: http://localhost:8000        (Weaver Dashboard)
#    Tab 2: http://localhost:8080        (Mock University Site)
#    Tab 3: http://localhost:8000/items  (Raw API JSON)

# 5. Open Telegram — chat with @HermesWeaverBot ready
# 6. Font size: terminal 16pt, browser zoom 110%
# 7. Screen resolution: 1920x1080
```

---

## Scene 1 — The Problem (0:00 – 0:12)

**Screen:** Show a simple split — left side: university website, right side: broken terminal

**Narration:**
> "Web scrapers break constantly. A website renames one CSS class — and your entire data pipeline goes down."

**Actions:**
1. Show `mock-site/index_working.html` in browser — clean university announcements page
2. Switch to terminal, show a `curl http://localhost:8000/items` that returns data
3. Briefly show `curl http://localhost:8000/items` returning `503 Service Unavailable` (after swapping HTML)

**Cut at:** 0:12

---

## Scene 2 — The Solution: Telegram → Live API (0:12 – 0:35)

**Screen:** Telegram chat with @HermesWeaverBot

**Narration:**
> "Weaver is a Hermes Agent skill. You give it a URL — it inspects the real DOM, writes the code, deploys the API, and monitors it. No manual configuration."

**Actions:**
1. Type in Telegram:
   ```
   Build an API for http://localhost:8080
   ```
2. Wait — show the bot thinking (no intermediate messages)
3. Bot replies with single message:
   ```
   ✅ Weaver API is live!
   📡 http://localhost:8000/items — 6 items
   🏥 http://localhost:8000/health
   👁 Monitoring every 30s
   ```

**Cut at:** 0:35

---

## Scene 3 — Live Dashboard (0:35 – 0:48)

**Screen:** Switch to browser, open `http://localhost:8000`

**Narration:**
> "Every generated API comes with a real-time dashboard — status, scraped items, and a full heal event log."

**Actions:**
1. Show the Weaver dashboard — dark theme, 6 items listed, status badge "Healthy"
2. Click `/items` endpoint chip — raw JSON appears in new tab
3. Pan back to dashboard, hover over a few item rows

**Cut at:** 0:48

---

## Scene 4 — Breaking the Site (0:48 – 1:00)

**Screen:** Terminal

**Narration:**
> "Now let's simulate what happens when the site updates its HTML — renaming CSS classes."

**Actions:**
1. Run in terminal:
   ```bash
   cp mock-site/index_broken.html mock-site/index.html
   ```
2. Switch to browser — refresh `http://localhost:8080` — site visually looks the same
3. Run:
   ```bash
   curl -s http://localhost:8000/items
   ```
4. Show `503 Service Unavailable` response in terminal — red highlight

**Cut at:** 1:00

---

## Scene 5 — Autonomous Self-Heal (1:00 – 1:25)

**Screen:** Split — Telegram (left) + Dashboard (right)

**Narration:**
> "The health monitor detects the failure. Weaver fetches the new DOM, identifies the renamed selectors, rewrites the scraper, and hot-swaps it — all without human intervention."

**Actions:**
1. Wait for Telegram notification to arrive:
   ```
   ⚠️ API broken — /items returning 503
   🔧 DOM fingerprint changed: cards=6 → cards=0|items=6
   Self-healing now...
   ```
2. After ~15 seconds, second Telegram message:
   ```
   ✅ Healed in 14s
   .announcement-card → .ann-item
   Schema v1.0.0 preserved. API restored.
   ```
3. Switch to dashboard — refresh — status badge flips to "Healthy", heal event appears in log

**Cut at:** 1:25

---

## Scene 6 — Verification (1:25 – 1:35)

**Screen:** Terminal

**Narration:**
> "Same endpoint. Same schema. Same field names. Zero data loss."

**Actions:**
1. Run:
   ```bash
   curl -s http://localhost:8000/items | python3 -m json.tool | head -20
   ```
2. Show `count: 6`, `schema_version: "1.0.0"`, and a real item with `title`, `category`, `date`
3. Zoom in on `schema_version: "1.0.0"` — circle it or highlight

**Cut at:** 1:35

---

## Scene 7 — Closing (1:35 – 1:45)

**Screen:** Weaver Dashboard full screen

**Narration:**
> "Weaver. Any URL becomes a self-healing API — powered by Hermes Agent."

**Actions:**
1. Show dashboard with heal event in the log panel
2. Fade to black with text overlay:
   ```
   ⚡ Weaver
   github.com/mehmetkr-31/hermes-apiaas
   Built with Hermes-4-405B · Nous Research Hackathon 2025
   ```

**End at:** 1:45

---

## Recording Tips

| Tip | Detail |
|-----|--------|
| **Hide terminal prompt** | Use `PS1="$ "` before recording |
| **Clear history noise** | `clear` before each scene |
| **Slow down typing** | Type Telegram message slowly — viewers need to read it |
| **Pause on results** | Hold 2 seconds on any JSON or dashboard result |
| **Dashboard zoom** | 110% browser zoom makes cards readable on video |
| **Audio** | Record narration separately — easier to edit |
| **Cuts** | Hard cuts between scenes, no transitions — keeps pace tight |

---

## Backup: If Telegram bot is slow

Run the demo with the CLI script instead:

```bash
cd ~/HERMES/hermes-apiaas
./agent/.venv/bin/python demo_heal.py
```

This runs the full self-healing flow in the terminal — works as a standalone demo without Telegram.

---

## Quick Reset Between Takes

```bash
cd ~/HERMES/hermes-apiaas
pkill -f uvicorn; pkill -f "server.py"
cp agent/scraper_v1.py agent/scraper.py
cp mock-site/index_working.html mock-site/index.html
rm -f agent/state.json agent/heal_log.jsonl agent/backups/*
echo "✓ Reset complete"
```
