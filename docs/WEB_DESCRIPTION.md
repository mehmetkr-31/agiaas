# Web Skills

Tools for automated web data extraction, API generation, and site monitoring.

Skills in this category enable the agent to turn any website into a structured
data pipeline — from one-shot scraping to continuously self-healing REST APIs.

## Available Skills

| Skill | Description |
|-------|-------------|
| [weaver](./weaver/SKILL.md) | Autonomous web scraping API generator and self-healer |

## When to Use Web Skills vs Built-in Tools

| Task | Better Choice | Why |
|------|--------------|-----|
| Quick one-off lookup | `web_search` or `web_extract` | Faster, no deployment needed |
| Recurring data extraction | **Weaver** | Generates a persistent, monitored API |
| Site structure changed, API broken | **Weaver self-heal** | Autonomously rewrites selectors |
| Need structured JSON from a URL | **Weaver** | Produces typed Pydantic schema |
| Just reading a page once | `web_extract` | Overkill to deploy an API |