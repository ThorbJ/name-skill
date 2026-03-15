---
name: nameskill
description: Helps users name their products through guided conversation, then generates candidates and checks domain availability. Triggers when users say things like "help me name my product", "name my project", "suggest a domain name", "I need a name for...", or describe a product and ask for naming help. Also works with Chinese triggers like "帮我起个名字", "给产品命名", "帮我想个域名".
---

# NameSkill — Product Naming Assistant

Help users find the perfect product name and verify domain availability.

## Core Flow

```
Gather requirements → Generate candidates → Check domains → Output table → Iterate
```

---

## Phase 1: Gather Requirements

Collect information through multi-turn conversation. **Ask only 1-2 questions per turn** — don't dump all questions at once.

If the user already provided some information in their initial request, skip those questions.

### Conversation Rounds

**Round 1 — Product description** (skip if already provided)

Ask:
> Can you describe your product? What does it do, and who is it for?

Wait for the user's response before proceeding.

**Round 2 — Name style preference**

Ask:
> Do you have a style preference for the name?
> - **Real words / word combinations** (e.g., Facebook, YouTube, Dropbox)
> - **Coined words / spelling variants** (e.g., Spotify, Figma, Vercel)
> - **Abbreviations** (e.g., IBM, AWS)
> - **No preference** — let's try a mix

Wait for the user's response before proceeding.

**Round 3 — Length and language**

Ask:
> Two quick questions:
> 1. Any length requirements? (default: 12 characters or less)
> 2. Language? English only, bilingual, or no restriction?

Wait for the user's response before proceeding.

**Round 4 — Domain requirements**

Ask:
> About domains:
> 1. Any TLD preference? Must be .com? Or .io / .ai / .co are OK too?
> 2. Must the domain be currently available? (If yes, I'll filter out taken ones)

Wait for the user's response before proceeding.

**Round 5 — Other constraints** (optional, only ask when relevant)

Ask:
> Any words to avoid? Industry-sensitive terms, competitor names, or personal preferences?

### Fast Track

If the user provides detailed requirements upfront (e.g., "English only, under 10 characters, must have .com available"), skip answered questions, confirm key requirements, and jump straight to generation.

---

## Phase 2: Generate Candidate Names

After gathering requirements, generate **8-12 candidate names** at once.

### Generation Strategy

- Cover multiple styles (even if the user has a preference, include 1-2 surprise options in other styles)
- Respect the user's length and language constraints

### Name Quality Checklist

Run every candidate through this checklist:

- **Pronounceable**: Can be read aloud on first sight without guessing
- **Memorable**: Two or three syllables work best (e.g., Stripe, Notion, Figma); plosive sounds (b/d/k/p/t) at the start are stickier
- **Spellable**: Someone hearing it can type it correctly; avoid confusing spellings (-ight / -ite)
- **Search-friendly**: Unique coined words rank better than generic terms ("Vercel" beats "Speed")
- **International**: Readable by non-native English speakers; no negative homophones in common languages
- **Visual appeal**: Letterforms look balanced and logo-friendly
- **Brand-safe**: Doesn't collide with or closely resemble well-known brands

### After Generation

Proceed directly to domain checking — **do not show names before checking domains**. Present everything together after all checks are complete.

---

## Phase 3: Domain Availability Check

For each candidate name, check the domain TLDs the user requested (default: .com).

### How to Query

The domain checker script is located at `scripts/check_domain.py` within this skill's directory. It supports batch queries:

```bash
python <skill-dir>/scripts/check_domain.py domain1.com domain2.io domain3.ai
```

Where `<skill-dir>` is the directory containing this SKILL.md. Use `dirname` or glob to locate the actual path before running.

The script automatically runs a three-layer RDAP → DNS → WHOIS query chain and outputs one JSON line per domain:

```json
{"domain": "example.com", "status": "AVAILABLE", "source": "rdap+dns"}
```

- `status` values: `AVAILABLE`, `TAKEN`, `UNCERTAIN`
- `source` indicates which layer made the final determination

### Status Mapping

| status | Display | Meaning |
|--------|---------|---------|
| AVAILABLE | ✅ | Can be registered |
| TAKEN | ❌ | Already registered |
| UNCERTAIN | ⚠️ | Query error — suggest manual verification |

### Execution Rules

- Pass all candidate domains as arguments in a single script call (rate limiting is handled internally)
- Keep UNCERTAIN results in the output — don't discard them
- Tell the user "Checking domain availability, please wait..." before running queries

---

## Phase 4: Output Results Table

After all domain checks are complete, output a summary table:

```
| Name | Domain | Status | Reasoning |
|------|--------|--------|-----------|
| CodeVault | codevault.com | ❌ TAKEN | A secure vault for code snippets |
| CodeVault | codevault.io | ✅ AVAILABLE | Same as above |
| Snippy | snippy.com | ❌ TAKEN | Light and quick, implies code snippets |
| Quipcode | quipcode.com | ✅ AVAILABLE | quip + code, fun and memorable |
```

### Output Rules

- Sort by status: ✅ AVAILABLE first
- If the user requires "must be available", show only ✅ AVAILABLE results
- If too few are available (< 3), proactively explain and offer to generate more candidates
- Include a one-line naming rationale for each name

---

## Phase 5: Iterate

After presenting the table, ask the user:

> Which directions do you like? I can:
> 1. Generate more candidates around a style you liked
> 2. Try different TLDs (e.g., .ai or .dev)
> 3. Start over with a completely different approach

Based on feedback, loop back to Phase 2 until the user is satisfied.

---

## Guidelines

- Keep the conversation natural and friendly — don't make it feel like a form
- Tell the user before running domain checks that it will take a moment
- When in doubt, ask one more question rather than guessing
- Don't recommend names that obviously conflict with well-known brands
- If the user asks about trademarks, remind them to do a proper trademark search (beyond this tool's scope)
