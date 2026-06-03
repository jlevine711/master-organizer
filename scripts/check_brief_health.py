#!/usr/bin/env python3
"""Health check for the Daily Brief archive.

Scans the `briefs/` directory and reports which recent days are missing an
archived brief (`briefs/<YYYY-MM-DD>.md`). The Daily Brief runs every morning
(including weekends), so every day in the window is expected to have a file.

Intended uses:
  * Run at the START of each Daily Brief run so a gap (a day the Routine
    silently failed to fire) is surfaced in the run's report instead of going
    unnoticed.
  * Run on demand to answer "did the brief run every day this week?".

Standard library only (no pip installs), same as send_brief.py.

Exit codes:
    0  no gaps in the window (today present, nothing missing)
    1  today's brief is missing  -> the caller should generate it now
    2  earlier day(s) missing but today is present  -> backfill gap(s)
"""
import argparse
import datetime as dt
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def central_today():
    """Resolve 'today' in America/Chicago without external deps."""
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo("America/Chicago")).date()
    except Exception:
        # Fallback: assume the process TZ is already Central (the Routine sets it).
        return dt.date.today()


def find_missing(briefs_dir, today, days):
    """Return the list of YYYY-MM-DD strings missing a brief file in the window."""
    missing = []
    for offset in range(days - 1, -1, -1):
        day = today - dt.timedelta(days=offset)
        iso = day.isoformat()
        if not os.path.isfile(os.path.join(briefs_dir, iso + ".md")):
            missing.append(iso)
    return missing


def main():
    ap = argparse.ArgumentParser(description="Report missing Daily Brief archives.")
    ap.add_argument("--briefs-dir", default=os.path.join(REPO_ROOT, "briefs"),
                    help="Directory holding <YYYY-MM-DD>.md archives.")
    ap.add_argument("--days", type=int, default=7,
                    help="How many days back (including today) to check. Default 7.")
    ap.add_argument("--today", help="Override today's date (YYYY-MM-DD) for testing.")
    args = ap.parse_args()

    today = (dt.date.fromisoformat(args.today) if args.today else central_today())
    missing = find_missing(args.briefs_dir, today, args.days)

    iso_today = today.isoformat()
    if not missing:
        print(f"OK: all {args.days} day(s) through {iso_today} have an archived brief.")
        return 0

    print(f"MISSING {len(missing)} of last {args.days} day(s): " + ", ".join(missing),
          file=sys.stderr)
    if iso_today in missing:
        print(f"-> today ({iso_today}) has no brief; generate it now.", file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
