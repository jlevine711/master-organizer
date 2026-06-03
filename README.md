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
on**, and then **emails it to you from your own address**. A markdown copy is archived to
`briefs/<date>.md`.

> **How it sends.** The Anthropic Gmail connector can only *create drafts*, so auto-send uses the
> **Gmail API** (`scripts/send_brief.py`) to send from your own address — it lands in your inbox and
> phone at 6 AM. This needs a one-time credential setup (below). **Until that's configured, the brief
> automatically falls back to a Gmail draft** so you always get one; finish the setup to flip it to a
> real send.

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
3. **Repository:** `jlevine711/master-organizer` — **Branch:** pin a **fixed** branch (e.g. `main`).
   ⚠️ **Do not leave the branch auto-generated.** If the Routine isn't pinned, each morning's run
   lands on a throwaway per-run branch, which (a) scatters the `briefs/` archive across dozens of
   branches and (b) means a day the job silently skips leaves no visible gap. Pin one branch so every
   brief accumulates there and the health check (below) can spot a miss.
4. **Connectors:** keep **Google Calendar, Gmail, Granola, and Plaud** enabled (Surfe not needed).
5. **Schedule:** Daily, **06:00**, timezone **America/Chicago**.
6. **Permissions:** confirm they match `.claude/settings.json` (the four `mcp__…__*` connectors plus
   `git`/`date`/`python3`/`Write`) so the run is fully unattended with no approval prompts.
7. Save. The first scheduled run delivers tomorrow's brief.

Each run shows up in your session list at claude.ai/code, so you can open the transcript to see
exactly what it did. **If a brief ever doesn't arrive, check that run's session first** — a missing
session means the schedule didn't fire (a platform-side miss, not a code/credential fault); just run
`/daily-brief` once to deliver that day.

### Did it run every day? (health check)

Each run starts by checking the archive for gaps. You can run the same check anytime:

```bash
python3 scripts/check_brief_health.py --days 7
```

It lists any of the last 7 days that have no `briefs/<date>.md` (exit `0` = all present, `1` = today
missing, `2` = an earlier day missing). This only works when the Routine is pinned to one branch (see
step 3) so all briefs live in the same place.

## One-time setup: enable auto-send (Gmail API)

This lets the brief send from your own address. Do it once (≈15 min). Until then, the brief still
arrives — as a Gmail draft.

**1. Create OAuth credentials** in [Google Cloud Console](https://console.cloud.google.com), signed in
as `jlevine@jalstrategies.com`:
- Create/select a project → **APIs & Services → Library** → enable **Gmail API**.
- **OAuth consent screen** → choose **Internal** (you're on Google Workspace, so the refresh token
  won't expire) → add the scope `https://www.googleapis.com/auth/gmail.send`.
- **Credentials → Create credentials → OAuth client ID → Web application.** Add the authorized
  redirect URI `https://developers.google.com/oauthplayground`. Save the **Client ID** and **Client
  secret**.

**2. Mint a refresh token** (no code) via the [OAuth Playground](https://developers.google.com/oauthplayground):
- Click the gear (top-right) → check **Use your own OAuth credentials** → paste your Client ID/secret.
- In the left scope box enter `https://www.googleapis.com/auth/gmail.send` → **Authorize APIs** →
  sign in as `jlevine@` and consent.
- Click **Exchange authorization code for tokens** → copy the **Refresh token**.

**3. Add three environment secrets** to the environment your Routine runs in (see
[environment config](https://code.claude.com/docs/en/claude-code-on-the-web)):
`GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, `GMAIL_REFRESH_TOKEN`.

**4. Network:** make sure the environment's network policy allows HTTPS to `oauth2.googleapis.com` and
`gmail.googleapis.com` (the default *Trusted* policy does).

Test it anytime with:
```bash
python3 scripts/send_brief.py --subject "Test" --html-file /tmp/x.html --text-file /tmp/x.txt
```
(`SENT id=…` means it worked; exit code 2 means the secrets aren't set yet.)

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
scripts/send_brief.py          # sends the brief from your own address (Gmail API)
scripts/check_brief_health.py  # flags days missing a brief archive (catches silent misses)
briefs/<YYYY-MM-DD>.md         # dated archive of each morning's brief
```
