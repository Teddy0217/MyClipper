# MyClipper — AI News Clipping Agent powered by CherryStudio and Exa Search

A local-first, AI-powered news clipping assistant built on [Exa's Search API](https://exa.ai) via MCP (Model Context Protocol). It fetches, enriches, and archives news articles as structured Markdown into an Obsidian vault, orchestrated through [CherryStudio](https://github.com/CherryHQ/cherry-studio).

## How Exa Is Used

Exa is the core search & retrieval engine of this project:

- **`web_search_exa`** — Bilingual semantic search (CN + EN) to find relevant sources for every clipping topic. Every topic triggers at least two rounds of Exa search across languages to maximize coverage.
- **`crawling_exa`** — Full content extraction from URLs. Primary method for fetching article body before any processing.
- **`deep_search_exa`** — Deep research mode for complex topics that require multi-angle information synthesis (e.g., event timelines, policy analysis).

The agent relies on Exa MCP as its **sole web access layer** — all internet-facing operations (search, fetch, crawl) route through Exa's API.

## Features

- **Clip**: Fetch URL via Exa → bilingual web search for context → generate structured Markdown reading note
- **Topic Research**: Deep search across CN + EN sources → synthesize event timelines and background analysis
- **Search**: Full-text and tag-based search across local clipping index
- **Tag Management**: Curated tag pool — `entity` (people, orgs, products) and `topic` (themes, events)
- **Auto-linking**: Entities wrapped in `[[wikilinks]]` for Obsidian graph navigation

## Architecture

```
myClipper/
├── index.json          # Flat-array clipping index
├── tags_pool.json      # Tag pool (entity / topic)
├── clippings/          # Archived .md reading notes
├── logs/               # Runtime logs
├── .claude/            # Agent prompts & commands
└── scripts/
    ├── init.py             # Bootstrap directories and data files
    ├── save_clipping.py    # Register clipping metadata to index
    ├── search_index.py     # Query the index
    ├── read_clipping.py    # Read a specific .md file
    ├── manage_tags.py      # CRUD for tag pool
    ├── fix_index.py        # Index health check & repair
    └── utils.py            # Shared utilities
```

## Tech Stack

| Layer | Tool |
|-------|------|
| **Search & Retrieval** | [Exa Search API](https://exa.ai) — semantic search, content extraction, deep research |
| **MCP Runtime** | Exa MCP Server — bridges LLM tool-use to Exa API |
| **Scripting** | Python (index management, tag system, file I/O) |
| **Chat Interface** | CherryStudio (tool-use orchestration) |
| **Knowledge Base** | Obsidian (Markdown vault, graph view, wikilinks) |

## Design Principles

- **Exa-native**: All web search and content retrieval goes through Exa's semantic search — no legacy scraping or keyword-matching
- **Bilingual by default**: Every search fires CN + EN queries via Exa to avoid single-language blind spots
- **Local-first**: All data stored as flat JSON + Markdown — no cloud database
- **Human-in-the-loop**: All file operations require user preview and confirmation

## Status

🚧 Active development — currently expanding Exa API integration to support more search categories and structured data extraction.
