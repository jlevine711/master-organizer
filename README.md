# master-organizer

Personal automation hub for **Justin A. Levine** (JAL Strategies). Its flagship automation is the
**Daily Brief** — a well-formatted email, generated every morning at **6:00 AM Central**, that gives
you today's calendar and a prioritized to-do list pulled from four connected tools.

## What the Daily Brief does

Each morning it reads, dedupes, and prioritizes across **four connectors**:

| Source | Connector | What it contributes |
|--------|-----------|---------------------|
| Today's schedule + meeting prep | **Google Calendar** | Every event today with times, join links, attendees |
| Email follow-ups you owe | **Gmail** | Open threads awaiting your reply or a decision |
| Meeting action items | **Granola** | Commitments/follow-ups from recent meeting notes |
| Recording action items | **Plaud** | To-dos extracted from recent recordings |

It groups everything by deal/topic (so *Shoppes at San Felipe* isn't repeated four times), surfaces
**Top Priorities** with hard dates, separates **business vs. personal**, lists **who you're waiting
on**, and then saves the result as a **Gmail draft** addressed to you. A markdown copy is archived to
`briefs/<date>.md`.

> **Why a draft and not a sent email?** The Gmail connector can only *create drafts* — it has no send
> capability. So each morning the brief lands in **Gmail → Drafts**. Read it there, or tap **Send** to
> push it to your inbox (and phone notification). If a send-capable email tool is added later, switch
> Step 7 of the command from `create_draft` to send.

## Run it on demand

In any Claude Code session on this repo:

```
/daily-brief
```

The full procedure lives in `.claude/commands/daily-brief.md`.

## One-time setup: schedule it for 6:00 AM Central (Routine)

Recurring runs use a **Routine**, which must be created in the web UI — it can't be created from
inside a session. Do this once:

1. Go to **https://claude.ai/code/routines** → **New routine**.
2. **Prompt:** `/daily-brief`
3. **Repository:** `jlevine711/master-organizer` — **Branch:** `claude/nifty-gates-oMuaa`
   (or `main` once this is merged).
4. **Connectors:** keep **Google Calendar, Gmail, Granola, and Plaud** enabled (Surfe not needed).
5. **Schedule:** Daily, **06:00**, timezone **America/Chicago**.
6. **Permissions:** confirm they match `.claude/settings.json` (the four `mcp__…__*` connectors plus
   `git`/`date`/`Write`) so the run is fully unattended with no approval prompts.
7. Save. The first scheduled run will create tomorrow's draft.

Each run shows up in your session list at claude.ai/code, so you can open the transcript to see
exactly what it did.

## Customizing

- **Sources, scope, tone, recipient:** edit `CLAUDE.md`.
- **Procedure / email layout:** edit `.claude/commands/daily-brief.md`.
- **Send time:** change it in the Routine (web UI).
- **Permissions for unattended runs:** `.claude/settings.json`.

## Layout

```
CLAUDE.md                      # owner defaults, connectors, to-do rules, scope
README.md                      # this file
.claude/settings.json          # pre-authorized tools for unattended Routine runs
.claude/commands/daily-brief.md# the Daily Brief procedure (/daily-brief)
briefs/<YYYY-MM-DD>.md         # dated archive of each morning's brief
```
