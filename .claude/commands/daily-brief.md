---
description: Generate Justin's Daily Brief (today's calendar + prioritized to-dos from Calendar, Gmail, Granola, Plaud) and save it as a Gmail draft + dated archive.
---

# Daily Brief

You are generating **Justin A. Levine's Daily Brief** — a single, well-formatted email that gives him
**today's schedule** and a **prioritized to-do list**, synthesized from four connectors. Follow these
steps exactly. Be accurate, concise, and executive in tone. No emojis. Resolve everything in
**America/Chicago** time.

Read `CLAUDE.md` first for owner defaults, the connector table, the "what counts as a to-do" rules,
and the business/personal scope rule. The MCP server ids referenced below come from that table.

---

## Step 0 — Resolve dates (Central time)

Run these and use the results throughout:

```bash
TZ="America/Chicago" date "+%Y-%m-%d"            # TODAY (e.g. 2026-05-26)
TZ="America/Chicago" date "+%A, %B %-d, %Y"      # PRETTY (e.g. Tuesday, May 26, 2026)
TZ="America/Chicago" date -d "tomorrow" "+%Y-%m-%d"   # TOMORROW (window end)
TZ="America/Chicago" date -d "7 days ago" "+%Y-%m-%d" # LOOKBACK start
TZ="America/Chicago" date "+%Y-%m-%d %-I:%M %p %Z"    # NOW (footer timestamp)
```

## Step 1 — Today's calendar (the "schedule")

Call `mcp__4d2add4c-bd75-44d7-9946-6429d5df9419__list_events` with
`startTime=<TODAY>T00:00:00`, `endTime=<TOMORROW>T00:00:00`, `timeZone="America/Chicago"`,
`orderBy="startTime"`, `pageSize=25`.

For each event capture: start–end (Central), title, attendees (name/email + who organized),
and the **join link** (parse the Google Meet / Microsoft Teams / Zoom URL out of `location` or the
HTML `description`). Note any **back-to-back** blocks and notable **open gaps**. For each external
meeting, derive a short **prep to-do** (e.g. "Pull latest figures before 2pm San Felipe DD call").

## Step 2 — Granola meeting action items

Call `mcp__f4d0adde-bb07-4e68-bc6c-d7ab4b30a999__query_granola_meetings` with a query like:
`"List open action items, follow-ups, and commitments from my meetings this week. Group by who owns each, and call out any hard deadlines."`

- Items **owned by Justin** → candidate to-dos.
- Items **owned by others** → **Waiting on / follow up**.
- **Preserve the citation links** Granola returns (`[[n]](url)`); render them as the source link.
- If more detail is needed on a specific meeting, use `list_meetings` then `get_meetings` by id.

## Step 3 — Plaud recording action items

Call `mcp__31fb401f-7142-4e4b-abfe-38eba609908f__list_files` with `date_from=<LOOKBACK>`,
`date_to=<TODAY>`. Take the most recent **~8** recordings. For each, call
`mcp__31fb401f-7142-4e4b-abfe-38eba609908f__get_note` and pull the `## To-Do List` /
`## Next Arrangements` checkbox items and any **hard dates** (e.g. "offer due June 4").

**Classify each recording business vs personal** by title/summary (see CLAUDE.md keywords:
therapy/therapist, family mediation, medical/doctor, family member names). Personal recordings'
action items go to the **Personal** section and must be reduced to **concrete, non-sensitive,
forward-looking actions only** (e.g. "Schedule next session," "Confirm Sunday timing") — never quote
therapy/medical content.

## Step 4 — Gmail open loops

Run a few targeted `mcp__5407b947-ddfa-4e38-968b-320f8989d99f__search_threads` queries
(`pageSize` ~15 each):
- `in:inbox is:unread newer_than:7d`
- `in:inbox is:starred`
- `in:inbox is:important newer_than:5d`

For each thread, look at the **latest message**. If it is **inbound (from someone else) and awaits
Justin's reply or action** — a question asked, a document requested, a decision needed — make it a
to-do, with the thread link `https://mail.google.com/mail/u/0/#all/<threadId>`. Skip threads where
Justin already sent the last message (those may instead be **Waiting on** the other party).
Use `get_thread` only when a snippet is too ambiguous to classify. Cap total Gmail to-dos at ~10.

## Step 5 — Synthesize, dedupe, prioritize, classify

- **Dedupe by deal/topic.** Collapse the same matter that appears across connectors into one group
  (e.g. *Shoppes at San Felipe* spans Calendar + Granola + Plaud + Gmail). Do **not** list the same
  task twice; merge and keep the best-sourced version with all relevant links.
- **Top Priorities (3–6):** rank by (a) hard deadlines, (b) prep for today's meetings, (c) decisions
  only Justin can make. Always surface the **date** for anything time-sensitive.
- Split everything into **Business** and **Personal**. Keep a **Waiting on / follow up** list for
  items others owe.

## Step 6 — Render the email (inline-CSS HTML + plain-text fallback)

Build **HTML with inline `style=` attributes only** (Gmail/Outlook strip `<style>` blocks and external
CSS). Constraints: a centered wrapper ~640px wide, system font stack
(`-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif`), restrained palette
(headings `#111827`, body `#374151`, hairlines `#e5e7eb`, section tint `#f8fafc`, deadline accent
`#b91c1c`). Make join links and source links real `<a href>`s. Use small uppercase "pills" for source
tags `[Calendar] [Email] [Granola] [Plaud]`.

Section order:
1. **Header** — "Daily Brief" + the pretty date.
2. **At a glance** — meeting count, first meeting time, and any hard deadline landing today.
3. **Today's schedule** — chronological rows: `time · title · join link · attendees`; flag conflicts/gaps.
4. **Top priorities** — the ranked 3–6, each with its source tag, link, and any date in the accent color.
5. **To-dos by deal/topic** — grouped; each line tagged with source pill(s) + link.
6. **Waiting on / follow up** — short list of who owes what.
7. **Personal** — clearly separated; forward-looking action items only.
8. **Footer** — "Generated <NOW> · auto-draft from master-organizer."

Also produce a **plain-text version** (same content, no markup) for the draft's `body` field so the
email degrades gracefully.

A minimal skeleton to follow (expand sections; keep all styles inline):

```html
<div style="margin:0;padding:24px 12px;background:#f1f5f9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
  <div style="max-width:640px;margin:0 auto;background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;">
    <div style="background:#111827;color:#ffffff;padding:20px 24px;">
      <div style="font-size:20px;font-weight:700;letter-spacing:.2px;">Daily Brief</div>
      <div style="font-size:13px;color:#cbd5e1;margin-top:2px;">Tuesday, May 26, 2026</div>
    </div>
    <div style="padding:8px 24px 24px;">
      <!-- At a glance -->
      <div style="margin-top:16px;padding:12px 14px;background:#f8fafc;border:1px solid #e5e7eb;border-radius:8px;font-size:14px;color:#374151;">
        <strong style="color:#111827;">At a glance:</strong> 3 meetings · first at 9:00 AM · <span style="color:#b91c1c;font-weight:600;">DD decision pending (San Felipe, ends Jul 2)</span>
      </div>
      <!-- Section pattern, repeat per section -->
      <h2 style="font-size:13px;text-transform:uppercase;letter-spacing:.6px;color:#6b7280;margin:24px 0 8px;">Today's schedule</h2>
      <!-- rows ... -->
    </div>
    <div style="padding:14px 24px;background:#f8fafc;border-top:1px solid #e5e7eb;font-size:12px;color:#9ca3af;">
      Generated <NOW> · auto-draft from master-organizer
    </div>
  </div>
</div>
```

Source-tag pill example (inline): `<span style="display:inline-block;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.4px;color:#475569;background:#e2e8f0;border-radius:4px;padding:1px 6px;margin-right:6px;">Email</span>`

## Step 7 — Create the draft

Call `mcp__5407b947-ddfa-4e38-968b-320f8989d99f__create_draft` with:
- `to`: `["jlevine@jalstrategies.com"]`
- `subject`: `"Daily Brief — <PRETTY date>"`  (e.g. `Daily Brief — Tuesday, May 26, 2026`)
- `htmlBody`: the HTML from Step 6
- `body`: the plain-text fallback from Step 6

Capture the returned draft id.

## Step 8 — Archive to the repo

Write the markdown version of the brief to `briefs/<TODAY>.md` (create the `briefs/` dir if needed),
then commit just that file so the archive persists across stateless Routine runs:

```bash
mkdir -p briefs
git add briefs/<TODAY>.md
git commit -m "Daily brief <TODAY>"
git push -u origin HEAD
```

If nothing changed (re-run on the same day with identical content), skip the commit.

## Step 9 — Report back

Print a 4–6 line summary to the session: the draft id, # meetings, # to-dos, the Top 3 priorities,
and the archive path. Remind Justin the draft is in **Gmail → Drafts** (tap Send to push it to his
inbox/phone).
