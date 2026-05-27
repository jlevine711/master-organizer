#!/usr/bin/env python3
"""Send Justin's Daily Brief from his own Gmail address via the Gmail API.

Standard library only (no pip installs). Reads OAuth credentials from the
environment so nothing secret lives in the repo:

    GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN
    (OAuth scope: https://www.googleapis.com/auth/gmail.send)

Exit codes:
    0  sent (or dry-run / --check-auth OK)
    2  credentials not configured  -> caller should fall back to a draft
    3  Gmail API / network error   -> caller should fall back to a draft
    4  bad usage (missing --subject/--html-file/--text-file for a send)

See README.md ("Enable auto-send") for how to mint the refresh token.
"""
import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

TOKEN_URL = "https://oauth2.googleapis.com/token"
SEND_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"


def read_text(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def build_raw(sender, to, subject, text, html):
    msg = MIMEMultipart("alternative")
    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = subject
    if text:
        msg.attach(MIMEText(text, "plain", "utf-8"))
    if html:
        msg.attach(MIMEText(html, "html", "utf-8"))
    return base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")


def get_access_token(client_id, client_secret, refresh_token):
    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request(TOKEN_URL, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.loads(resp.read().decode())
    token = payload.get("access_token")
    if not token:
        raise RuntimeError("token endpoint returned no access_token")
    return token


def send_message(access_token, raw):
    body = json.dumps({"raw": raw}).encode()
    req = urllib.request.Request(SEND_URL, data=body, method="POST")
    req.add_header("Authorization", "Bearer " + access_token)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def read_creds():
    cid = os.environ.get("GMAIL_CLIENT_ID")
    secret = os.environ.get("GMAIL_CLIENT_SECRET")
    rtoken = os.environ.get("GMAIL_REFRESH_TOKEN")
    missing = [name for name, val in (
        ("GMAIL_CLIENT_ID", cid),
        ("GMAIL_CLIENT_SECRET", secret),
        ("GMAIL_REFRESH_TOKEN", rtoken),
    ) if not val]
    return cid, secret, rtoken, missing


def check_auth():
    """Verify the GMAIL_* creds mint an access token. Sends nothing, prints no secret."""
    cid, secret, rtoken, missing = read_creds()
    if missing:
        print("ERROR: auto-send not configured; missing env var(s): "
              + ", ".join(missing), file=sys.stderr)
        return 2
    try:
        token = get_access_token(cid, secret, rtoken)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        print(f"ERROR: token exchange HTTP {exc.code}: {detail}", file=sys.stderr)
        return 3
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3
    print(f"AUTH OK: refresh token valid; minted an access token ({len(token)} chars). No email sent.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Send the Daily Brief via the Gmail API.")
    ap.add_argument("--subject")
    ap.add_argument("--to", default="jlevine@jalstrategies.com")
    ap.add_argument("--sender", default="jlevine@jalstrategies.com")
    ap.add_argument("--html-file")
    ap.add_argument("--text-file")
    ap.add_argument("--dry-run", action="store_true",
                    help="Build the MIME message but do not contact Google (no creds needed).")
    ap.add_argument("--check-auth", action="store_true",
                    help="Verify the GMAIL_* credentials mint an access token; send nothing.")
    args = ap.parse_args()

    if args.check_auth:
        return check_auth()

    missing_args = [name for name, val in (
        ("--subject", args.subject),
        ("--html-file", args.html_file),
        ("--text-file", args.text_file),
    ) if not val]
    if missing_args:
        print("ERROR: missing required argument(s): " + ", ".join(missing_args),
              file=sys.stderr)
        return 4

    html = read_text(args.html_file)
    text = read_text(args.text_file)
    raw = build_raw(args.sender, args.to, args.subject, text, html)

    if args.dry_run:
        print(f"[dry-run] from={args.sender} to={args.to} subject={args.subject!r}")
        print(f"[dry-run] base64url raw length={len(raw)} chars; message is well-formed.")
        return 0

    cid, secret, rtoken, missing = read_creds()
    if missing:
        print("ERROR: auto-send not configured; missing env var(s): "
              + ", ".join(missing), file=sys.stderr)
        return 2

    try:
        token = get_access_token(cid, secret, rtoken)
        result = send_message(token, raw)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        print(f"ERROR: Gmail API HTTP {exc.code}: {detail}", file=sys.stderr)
        return 3
    except Exception as exc:  # network, JSON, etc. -> let caller fall back
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3

    print(f"SENT id={result.get('id')} threadId={result.get('threadId')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
