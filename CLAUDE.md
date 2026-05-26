# master-organizer

Personal automation hub for **Justin A. Levine** — Founder, JAL Strategies (commercial real estate
acquisitions, Houston TX). The flagship automation is a **Daily Brief**: a well-formatted email,
generated every morning, that combines today's calendar with a prioritized to-do list pulled from
several connected tools.

## Owner & defaults

- **Name:** Justin A. Levine — Founder, JAL Strategies
- **Timezone:** `America/Chicago` (Central). Always resolve "today" in Central time.
- **Brief recipient:** `jlevine@jalstrategies.com` (secondary address: `jal@jalstrategicholdings.com`).
- **Tone:** concise, executive, skimmable. No emojis.

## Connectors (MCP servers available in every session, incl. scheduled Routines)

| Role | Connector | Server id (use in `mcp__<id>__<tool>`) | Primary tools |
|------|-----------|----------------------------------------|---------------|
| Calendar / schedule | Google Calendar | `4d2add4c-bd75-44d7-9946-6429d5df9419` | `list_events`, `list_calendars` |
| Email (read + draft) | Gmail | `5407b947-ddfa-4e38-968b-320f8989d99f` | `search_threads`, `get_thread`, `create_draft` |
| Meeting action items | Granola | `f4d0adde-bb07-4e68-bc6c-d7ab4b30a999` | `query_granola_meetings`, `list_meetings`, `get_meetings` |
| Recording action items | Plaud | `31fb401f-7142-4e4b-abfe-38eba609908f` | `list_files`, `get_note`, `get_transcript` |

`Surfe` (prospect/business enrichment) is connected but **not used** by the Daily Brief.

> **Gmail constraint:** the Gmail connector can **create drafts only** — it has no send tool. The
> Daily Brief therefore writes a draft to Justin's own mailbox. He reads it in Drafts, or taps Send
> to push it to his inbox/phone.

## What counts as a "to-do"

- **Owned by Justin** and not yet done: decisions he must make, documents he must send, replies he
  owes, prep for today's meetings. These go in the to-do list / Top Priorities.
- Items **owned by other people** go under **"Waiting on / follow up"** (so he can chase them), not
  in his own to-do list.
- **Dedupe by deal/topic.** The same matter shows up across connectors (e.g. *Shoppes at San Felipe*
  appears in Calendar + Granola + Plaud + Gmail). Group it once; don't repeat the same task.
- **Hard dates win.** Anything with a deadline (offer due, rate-lock expiry, DD end date) is surfaced
  in Top Priorities with the date called out.

## Scope: business + personal (separated)

Include both business and personal items, but keep personal ones in a clearly-labeled **Personal**
section at the bottom. Classify a meeting/recording as **personal** when its title or summary involves:
therapy / therapist, family mediation, medical / doctor, or a family member's name. For personal
items, list only concrete forward-looking action items (e.g. "schedule next session") — keep
sensitive content out of the brief. Everything else is business.

## The Daily Brief

The procedure lives in `.claude/commands/daily-brief.md` and runs via `/daily-brief`. It is the prompt
the scheduled Routine executes each morning at **06:00 America/Chicago**. Each run also archives the
brief to `briefs/<YYYY-MM-DD>.md`. See `README.md` for the one-time Routine setup (web-UI step).

Permissions for unattended runs are pre-authorized in `.claude/settings.json`.
