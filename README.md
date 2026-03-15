# name-skill

A Claude Code skill that helps you name your product and checks domain availability — all through natural conversation.

## What it does

1. **Guided conversation** — Asks about your product, naming preferences, domain requirements
2. **Name generation** — Produces 8-12 candidates covering different styles
3. **Domain checking** — Verifies `.com` / `.io` / `.ai` availability using RDAP + DNS + WHOIS
4. **Results table** — Shows names with domain status (available / taken / uncertain) and reasoning

## Install

Copy the `nameskill/` folder into your Claude Code skills directory:

```bash
cp -r nameskill/ ~/.claude/skills/nameskill/
```

Then start a new Claude Code conversation. The skill will be loaded automatically.

## Usage

Just say something like:

- "帮我起个名字"
- "I'm building an AI writing assistant, help me name it"
- "给产品命名"
- "帮我想个域名"

The skill will guide you through the rest.

## Domain checker

The domain checking script can also be used standalone:

```bash
python nameskill/scripts/check_domain.py notion.com example.io myapp.ai
```

Output (one JSON per line):

```json
{"domain": "notion.com", "status": "TAKEN", "source": "rdap"}
{"domain": "myapp.ai", "status": "AVAILABLE", "source": "rdap+dns"}
```

### Three-layer query chain

| Layer | Method | Purpose |
|-------|--------|---------|
| 1 | RDAP | Primary lookup via `rdap.org` |
| 2 | DNS NS | Validates RDAP negatives against actual nameserver records |
| 3 | WHOIS | Fallback for TLDs not supported by RDAP |

### Requirements

- Python 3.9+
- `dig` command (pre-installed on macOS/Linux)
- `whois` command (pre-installed on macOS, `apt install whois` on Linux)
- No API keys needed

## License

MIT
