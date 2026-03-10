"""
Weaver Dashboard — Real-time API status, items, and heal events
Serves a beautiful HTML dashboard at GET /
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pathlib import Path
import json
from datetime import datetime

router = APIRouter()

HEAL_LOG   = Path(__file__).parent / "heal_log.jsonl"
STATE_FILE = Path(__file__).parent / "state.json"


def _load_state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}
    except Exception:
        return {}


def _load_heal_events(limit: int = 10) -> list:
    if not HEAL_LOG.exists():
        return []
    events = []
    try:
        lines = HEAL_LOG.read_text().strip().splitlines()
        for line in reversed(lines[-limit * 2:]):
            try:
                events.append(json.loads(line))
            except Exception:
                pass
        return events[:limit]
    except Exception:
        return []


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Weaver — Live API Dashboard</title>
  <style>
    :root {{
      --bg:        #0d1117;
      --surface:   #161b22;
      --surface2:  #21262d;
      --border:    #30363d;
      --accent:    #58a6ff;
      --green:     #3fb950;
      --red:       #f85149;
      --yellow:    #d29922;
      --purple:    #bc8cff;
      --text:      #e6edf3;
      --muted:     #8b949e;
      --radius:    12px;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      padding: 0 0 60px 0;
    }}

    /* ── Header ── */
    header {{
      background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
      border-bottom: 1px solid var(--border);
      padding: 20px 32px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 100;
      backdrop-filter: blur(10px);
    }}

    .logo {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .logo-icon {{
      width: 36px;
      height: 36px;
      background: linear-gradient(135deg, var(--accent), var(--purple));
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
    }}

    .logo-text h1 {{
      font-size: 1.2rem;
      font-weight: 700;
      letter-spacing: -0.5px;
    }}

    .logo-text span {{
      font-size: 0.75rem;
      color: var(--muted);
    }}

    .header-right {{
      display: flex;
      align-items: center;
      gap: 16px;
    }}

    .refresh-indicator {{
      font-size: 0.75rem;
      color: var(--muted);
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .refresh-dot {{
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--green);
      animation: pulse 2s infinite;
    }}

    @keyframes pulse {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0.3; }}
    }}

    /* ── Layout ── */
    main {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 32px 24px 0;
      display: grid;
      gap: 24px;
    }}

    /* ── Status Bar ── */
    .status-bar {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
    }}

    .stat-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 20px 24px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      transition: border-color 0.2s;
    }}

    .stat-card:hover {{
      border-color: var(--accent);
    }}

    .stat-label {{
      font-size: 0.72rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      color: var(--muted);
    }}

    .stat-value {{
      font-size: 1.9rem;
      font-weight: 700;
      letter-spacing: -1px;
      line-height: 1;
    }}

    .stat-sub {{
      font-size: 0.75rem;
      color: var(--muted);
      margin-top: 2px;
    }}

    .status-ok     {{ color: var(--green);  }}
    .status-broken {{ color: var(--red);    }}
    .status-healing{{ color: var(--yellow); }}
    .status-unknown{{ color: var(--muted);  }}

    /* ── Big Status Badge ── */
    .status-badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 14px;
      border-radius: 999px;
      font-size: 0.8rem;
      font-weight: 600;
      letter-spacing: 0.3px;
    }}

    .badge-ok      {{ background: rgba(63,185,80,0.15);  color: var(--green);  border: 1px solid rgba(63,185,80,0.3);  }}
    .badge-broken  {{ background: rgba(248,81,73,0.15);  color: var(--red);    border: 1px solid rgba(248,81,73,0.3);  }}
    .badge-healing {{ background: rgba(210,153,34,0.15); color: var(--yellow); border: 1px solid rgba(210,153,34,0.3); }}
    .badge-unknown {{ background: rgba(139,148,158,0.1); color: var(--muted);  border: 1px solid var(--border); }}

    .badge-dot {{
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: currentColor;
    }}

    .badge-ok .badge-dot {{ animation: pulse 2s infinite; }}

    /* ── Two-column grid ── */
    .two-col {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
    }}

    @media (max-width: 768px) {{
      .two-col {{ grid-template-columns: 1fr; }}
    }}

    /* ── Panel ── */
    .panel {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      overflow: hidden;
    }}

    .panel-header {{
      padding: 16px 20px;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .panel-title {{
      font-size: 0.85rem;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .panel-count {{
      font-size: 0.72rem;
      background: var(--surface2);
      border: 1px solid var(--border);
      padding: 2px 8px;
      border-radius: 999px;
      color: var(--muted);
    }}

    .panel-body {{
      padding: 0;
      max-height: 460px;
      overflow-y: auto;
    }}

    .panel-body::-webkit-scrollbar {{ width: 4px; }}
    .panel-body::-webkit-scrollbar-track {{ background: transparent; }}
    .panel-body::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 2px; }}

    /* ── Item Row ── */
    .item-row {{
      padding: 14px 20px;
      border-bottom: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      gap: 4px;
      transition: background 0.15s;
    }}

    .item-row:last-child {{ border-bottom: none; }}
    .item-row:hover {{ background: var(--surface2); }}

    .item-title {{
      font-size: 0.85rem;
      font-weight: 500;
      color: var(--text);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .item-meta {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }}

    .item-tag {{
      font-size: 0.7rem;
      color: var(--muted);
      display: flex;
      align-items: center;
      gap: 4px;
    }}

    .item-tag-accent {{ color: var(--accent); }}
    .item-tag-green  {{ color: var(--green);  }}
    .item-tag-purple {{ color: var(--purple); }}

    /* ── Heal Event Row ── */
    .heal-row {{
      padding: 14px 20px;
      border-bottom: 1px solid var(--border);
      display: flex;
      gap: 14px;
      align-items: flex-start;
      transition: background 0.15s;
    }}

    .heal-row:last-child {{ border-bottom: none; }}
    .heal-row:hover {{ background: var(--surface2); }}

    .heal-icon {{
      width: 30px;
      height: 30px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      flex-shrink: 0;
      margin-top: 2px;
    }}

    .heal-icon-ok      {{ background: rgba(63,185,80,0.15);  }}
    .heal-icon-start   {{ background: rgba(210,153,34,0.15); }}
    .heal-icon-abort   {{ background: rgba(248,81,73,0.15);  }}
    .heal-icon-health  {{ background: rgba(88,166,255,0.1);  }}

    .heal-info {{
      flex: 1;
      min-width: 0;
    }}

    .heal-event {{
      font-size: 0.82rem;
      font-weight: 500;
      color: var(--text);
    }}

    .heal-event-ok     {{ color: var(--green);  }}
    .heal-event-start  {{ color: var(--yellow); }}
    .heal-event-abort  {{ color: var(--red);    }}

    .heal-time {{
      font-size: 0.7rem;
      color: var(--muted);
      margin-top: 3px;
    }}

    .heal-detail {{
      font-size: 0.72rem;
      color: var(--muted);
      margin-top: 4px;
      font-family: 'SF Mono', 'Fira Code', monospace;
      background: var(--bg);
      padding: 4px 8px;
      border-radius: 6px;
      border: 1px solid var(--border);
    }}

    /* ── Endpoints strip ── */
    .endpoints {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 20px 24px;
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
    }}

    .endpoints-label {{
      font-size: 0.72rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      color: var(--muted);
      margin-right: 4px;
    }}

    .endpoint-chip {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 14px;
      background: var(--surface2);
      border: 1px solid var(--border);
      border-radius: 8px;
      font-size: 0.78rem;
      font-family: 'SF Mono', 'Fira Code', monospace;
      cursor: pointer;
      text-decoration: none;
      color: var(--accent);
      transition: border-color 0.15s, background 0.15s;
    }}

    .endpoint-chip:hover {{
      border-color: var(--accent);
      background: rgba(88,166,255,0.08);
    }}

    .method-badge {{
      font-size: 0.65rem;
      font-weight: 700;
      padding: 1px 5px;
      border-radius: 4px;
      background: rgba(88,166,255,0.15);
      color: var(--accent);
      letter-spacing: 0.5px;
    }}

    /* ── Empty state ── */
    .empty-state {{
      padding: 48px 24px;
      text-align: center;
      color: var(--muted);
    }}

    .empty-state-icon {{
      font-size: 2.5rem;
      margin-bottom: 12px;
    }}

    .empty-state p {{
      font-size: 0.85rem;
    }}

    /* ── Footer ── */
    .dash-footer {{
      text-align: center;
      padding: 32px;
      font-size: 0.75rem;
      color: var(--muted);
    }}

    .dash-footer a {{
      color: var(--accent);
      text-decoration: none;
    }}
  </style>
</head>
<body>

<header>
  <div class="logo">
    <div class="logo-icon">⚡</div>
    <div class="logo-text">
      <h1>Weaver</h1>
      <span>Autonomous Self-Healing API Engine</span>
    </div>
  </div>
  <div class="header-right">
    <div class="refresh-indicator">
      <div class="refresh-dot"></div>
      Live · refreshes every 10s
    </div>
    <div class="{badge_class}">
      <div class="badge-dot"></div>
      {status_label}
    </div>
  </div>
</header>

<main>

  <!-- Stats -->
  <div class="status-bar">
    <div class="stat-card">
      <div class="stat-label">API Status</div>
      <div class="stat-value {status_color}">{status_icon}</div>
      <div class="stat-sub">{status_text}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Items Scraped</div>
      <div class="stat-value" style="color:var(--accent)">{item_count}</div>
      <div class="stat-sub">from {source}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Selector Version</div>
      <div class="stat-value" style="color:var(--purple); font-size:1.4rem">{selector_version}</div>
      <div class="stat-sub">schema v1.0.0 locked</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Last Scrape</div>
      <div class="stat-value" style="color:var(--text); font-size:1rem; font-weight:500; letter-spacing:0">{last_scrape}</div>
      <div class="stat-sub">DOM · {dom_fingerprint}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Self-Heals</div>
      <div class="stat-value" style="color:var(--green)">{heal_count}</div>
      <div class="stat-sub">autonomous repairs</div>
    </div>
  </div>

  <!-- Endpoints -->
  <div class="endpoints">
    <span class="endpoints-label">Endpoints</span>
    <a class="endpoint-chip" href="/items" target="_blank">
      <span class="method-badge">GET</span>/items
    </a>
    <a class="endpoint-chip" href="/health" target="_blank">
      <span class="method-badge">GET</span>/health
    </a>
    <a class="endpoint-chip" href="/state" target="_blank">
      <span class="method-badge">GET</span>/state
    </a>
    <a class="endpoint-chip" href="/docs" target="_blank">
      <span class="method-badge">UI</span>/docs
    </a>
  </div>

  <!-- Items + Heal Log -->
  <div class="two-col">

    <!-- Items Panel -->
    <div class="panel">
      <div class="panel-header">
        <div class="panel-title">📄 Scraped Items</div>
        <span class="panel-count">{item_count} items</span>
      </div>
      <div class="panel-body">
        {items_html}
      </div>
    </div>

    <!-- Heal Log Panel -->
    <div class="panel">
      <div class="panel-header">
        <div class="panel-title">🔧 Heal Log</div>
        <span class="panel-count">{heal_event_count} events</span>
      </div>
      <div class="panel-body">
        {heal_html}
      </div>
    </div>

  </div>

</main>

<div class="dash-footer">
  Weaver ⚡ · Built with <a href="https://github.com/nousresearch/hermes-agent" target="_blank">Hermes Agent</a>
  · <a href="https://github.com/mehmetkr-31/hermes-apiaas" target="_blank">GitHub</a>
</div>

<script>
  // Auto-refresh every 10 seconds
  setTimeout(() => location.reload(), 10000);

  // Highlight item rows on load with stagger
  document.querySelectorAll('.item-row, .heal-row').forEach((el, i) => {{
    el.style.opacity = '0';
    el.style.transform = 'translateY(8px)';
    el.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    setTimeout(() => {{
      el.style.opacity = '1';
      el.style.transform = 'translateY(0)';
    }}, i * 40);
  }});
</script>

</body>
</html>"""


def _fmt_time(iso: str) -> str:
    """Format ISO timestamp to human-readable."""
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%H:%M:%S")
    except Exception:
        return iso[:16] if iso else "—"


def _fmt_event(event: dict) -> str:
    ev = event.get("event", "unknown")
    if ev == "heal_end":
        success = event.get("success", False)
        old_fp  = event.get("old_fingerprint", "?")
        new_fp  = event.get("new_fingerprint", "?")
        icon    = "✅" if success else "❌"
        label   = "Heal complete" if success else "Heal failed"
        icon_cls= "heal-icon-ok" if success else "heal-icon-abort"
        event_cls = "heal-event-ok" if success else "heal-event-abort"
        detail  = f"{old_fp} → {new_fp}" if success else "Selectors could not be updated"
        return (icon, icon_cls, label, event_cls, detail)
    elif ev == "heal_start":
        return ("🔧", "heal-icon-start", "Self-heal triggered", "heal-event-start",
                f"Failures: {', '.join(event.get('failures', []))}")
    elif ev == "heal_abort":
        return ("⚠️", "heal-icon-abort", "Heal aborted", "heal-event-abort",
                event.get("reason", "unknown"))
    elif ev == "health_ok":
        count = event.get("count", 0)
        fp    = event.get("fingerprint", "")
        return ("💚", "heal-icon-health", f"Health OK · {count} items", "", fp)
    else:
        return ("📋", "heal-icon-health", ev, "", "")


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def dashboard():
    state = _load_state()
    heal_events = _load_heal_events(limit=20)

    # Status
    raw_status = state.get("status", "unknown")
    # Try to determine status from state fields
    if not state:
        raw_status = "waiting"
    elif state.get("item_count", state.get("announcement_count", 0)) > 0:
        raw_status = "ok"
    else:
        raw_status = "unknown"

    if raw_status == "ok":
        status_color = "status-ok"
        status_icon  = "●"
        status_text  = "Healthy — serving live data"
        badge_class  = "status-badge badge-ok"
        status_label = "Healthy"
    elif raw_status in ("broken", "degraded"):
        status_color = "status-broken"
        status_icon  = "●"
        status_text  = "Broken — self-heal may be pending"
        badge_class  = "status-badge badge-broken"
        status_label = "Broken"
    elif raw_status == "healing":
        status_color = "status-healing"
        status_icon  = "◐"
        status_text  = "Healing — rewriting selectors…"
        badge_class  = "status-badge badge-healing"
        status_label = "Healing"
    else:
        status_color = "status-unknown"
        status_icon  = "○"
        status_text  = "Waiting for first scrape"
        badge_class  = "status-badge badge-unknown"
        status_label = "Waiting"

    item_count       = state.get("item_count", state.get("announcement_count", 0))
    source           = state.get("source", state.get("target_url", "unknown"))
    selector_version = state.get("selector_version", "v1")
    last_scrape_raw  = state.get("last_successful_scrape", "")
    last_scrape      = _fmt_time(last_scrape_raw) if last_scrape_raw else "—"
    dom_fingerprint  = state.get("dom_fingerprint", "—")

    # Heal count
    heal_count = sum(
        1 for e in heal_events
        if e.get("event") == "heal_end" and e.get("success")
    )

    # Items HTML — try to fetch from /items endpoint
    items_data = []
    try:
        import httpx as _httpx
        r = _httpx.get("http://localhost:8000/items", timeout=3)
        if r.status_code == 200:
            body = r.json()
            items_data = body.get("items", body.get("announcements", []))
    except Exception:
        pass

    if items_data:
        rows = []
        for it in items_data:
            title      = it.get("title", it.get("name", "—"))
            category   = it.get("category", "")
            department = it.get("department", it.get("responsible_entity", ""))
            date       = it.get("date", it.get("deadline", ""))
            excerpt    = it.get("excerpt", it.get("long_description", ""))[:80]
            rows.append(f"""
            <div class="item-row">
              <div class="item-title">{title}</div>
              <div class="item-meta">
                {"<span class='item-tag item-tag-accent'>📂 " + category + "</span>" if category else ""}
                {"<span class='item-tag item-tag-purple'>🏛️ " + department + "</span>" if department else ""}
                {"<span class='item-tag'>🕐 " + date + "</span>" if date else ""}
              </div>
              {"<div class='item-tag' style='margin-top:2px;font-size:0.7rem;color:var(--muted)'>" + excerpt + "</div>" if excerpt else ""}
            </div>""")
        items_html = "".join(rows)
    else:
        items_html = """
        <div class="empty-state">
          <div class="empty-state-icon">📭</div>
          <p>No items yet — waiting for first scrape</p>
        </div>"""

    # Heal log HTML
    if heal_events:
        rows = []
        for event in heal_events:
            icon, icon_cls, label, event_cls, detail = _fmt_event(event)
            ts = _fmt_time(event.get("ts", ""))
            detail_html = f'<div class="heal-detail">{detail}</div>' if detail else ""
            rows.append(f"""
            <div class="heal-row">
              <div class="heal-icon {icon_cls}">{icon}</div>
              <div class="heal-info">
                <div class="heal-event {event_cls}">{label}</div>
                <div class="heal-time">{ts}</div>
                {detail_html}
              </div>
            </div>""")
        heal_html = "".join(rows)
    else:
        heal_html = """
        <div class="empty-state">
          <div class="empty-state-icon">🕊️</div>
          <p>No heal events yet — system is stable</p>
        </div>"""

    html = HTML_TEMPLATE.format(
        badge_class      = badge_class,
        status_label     = status_label,
        status_color     = status_color,
        status_icon      = status_icon,
        status_text      = status_text,
        item_count       = item_count,
        source           = source,
        selector_version = selector_version,
        last_scrape      = last_scrape,
        dom_fingerprint  = dom_fingerprint,
        heal_count       = heal_count,
        items_html       = items_html,
        heal_html        = heal_html,
        heal_event_count = len(heal_events),
    )

    return HTMLResponse(content=html)
