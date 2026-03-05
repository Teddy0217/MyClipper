# MyClipper — AI News Clipping Agent

A local-first, AI-powered news clipping assistant that runs inside [CherryStudio](https://github.com/CherryHQ/cherry-studio). It fetches, enriches, and archives news articles as structured Markdown files into an Obsidian vault.

## What It Does

- **Clip**: Fetch a URL → extract content → enrich with bilingual web search (CN + EN) → generate a structured reading note in Markdown
- **Search**: Full-text and tag-based search across your clipping index
- **Tag Management**: Maintains a curated tag pool with two categories — `entity` (people, orgs, products) and `topic` (themes, events, domains)
- **Auto-linking**: Entities in notes are wrapped in `[[wikilinks]]` for Obsidian graph navigation

## Design Principles

- **Local-first**: All data (index, tags, clippings) stored as flat JSON + Markdown files — no database, no cloud dependency
- **Bilingual search**: Every topic is searched in both Chinese and English to maximize source coverage
- **Human-in-the-loop**: All file operations require user preview and confirmation before saving
- **Obsidian-native**: Output format, linking, and file naming are optimized for Obsidian vault workflows

## Architecture

```
myClipper/
├── index.json          # Flat-array clipping index
├── tags_pool.json      # Tag pool (entity / topic)
├── clippings/          # Archived .md reading notes
├── logs/               # Runtime logs
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

- Python (scripting layer)
- [Exa Search API](https://exa.ai) — semantic web search & content extraction (via MCP)
- CherryStudio — chat interface with tool-use support
- Obsidian — knowledge base & note viewer

## File Naming Convention

`YYYYMMDD-brief-description.md` — date-prefixed, concise Chinese summary (≤10 chars), English only for proper nouns (e.g., `20250615-OpenAI发布GPT-5.md`).

## Tag System

| Category | Examples |
|----------|---------|
| `entity` | OpenAI, 特朗普, ASML, 北京 |
| `topic`  | 中美关系, 芯片禁令, 大模型 |

Each clipping: 1–3 entities + 1–2 topics, max 5 tags total. New tags are created only when the existing pool cannot cover the content.

## Status

🚧 Active development — personal tool, not packaged for distribution.
