#!/usr/bin/env python3
"""
Rewrites the Monoleaf release line in README.md from the GitHub Releases API.

Run by .github/workflows/monoleaf-release.yml on a schedule, so the profile shows the
current version without anyone editing Markdown. Also runnable by hand.

The line lives between two HTML comments on the Monoleaf links row:

    [monoleaf.org](…) · [Source](…)<!-- MONOLEAF_RELEASE:START --><!-- MONOLEAF_RELEASE:END -->

Empty markers render as nothing, so the profile reads correctly before the first
release exists. That is the whole point of the marker pair: no placeholder text to
forget about.

FAILURE POSTURE: only a confirmed HTTP 200 rewrites anything. A 404 (repo private and
the token cannot see it, or no release published yet), a 403 (rate limit), or any
network error leaves README.md byte-for-byte untouched and exits 0. A transient API
problem must never blank out a correct line or wedge the workflow red.

Auth: set GH_TOKEN to a fine-grained PAT with Contents:read on the Monoleaf repo while
that repo is private. Once it is public, the workflow's default token suffices and the
secret can be deleted.

Run:  python scripts/update_release.py
"""
import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.request

REPO = "vibingbiochemist/Monoleaf"
START = "<!-- MONOLEAF_RELEASE:START -->"
END = "<!-- MONOLEAF_RELEASE:END -->"

README = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "README.md")


def fetch_latest():
    """The newest published release, or None if there isn't one we may read."""
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/releases/latest",
        headers={"Accept": "application/vnd.github+json",
                 "User-Agent": "profile-readme-release-tracker"},
    )
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as err:
        reason = {404: "no published release, or the token cannot see the repo",
                  403: "forbidden or rate-limited",
                  401: "bad or missing token"}.get(err.code, err.reason)
        print(f"{REPO}: HTTP {err.code} — {reason}. Leaving README.md untouched.")
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as err:
        print(f"{REPO}: could not reach the API ({err}). Leaving README.md untouched.")
    return None


def human_date(stamp: str) -> str:
    """'2026-08-02T09:15:00Z' -> '2 August 2026'. Falls back to the raw date."""
    try:
        day = datetime.datetime.strptime(stamp[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return (stamp or "")[:10]
    return f"{day.day} {day.strftime('%B %Y')}"


def main() -> int:
    release = fetch_latest()
    if release is None:
        return 0

    tag = (release.get("tag_name") or "").strip()
    if not tag:
        print("Release has no tag_name. Leaving README.md untouched.")
        return 0

    published = human_date(release.get("published_at", ""))
    line = f" &nbsp;·&nbsp; Latest release `{tag}`"
    if published:
        line += f" &nbsp;·&nbsp; {published}"

    with open(README, encoding="utf-8") as fh:
        text = fh.read()

    if START not in text or END not in text:
        print(f"Markers missing from README.md — expected {START} … {END}.",
              file=sys.stderr)
        return 1

    updated = re.sub(f"{re.escape(START)}.*?{re.escape(END)}",
                     lambda _: f"{START}{line}{END}",
                     text, count=1, flags=re.S)

    if updated == text:
        print(f"Already current: {tag}.")
        return 0

    with open(README, "w", encoding="utf-8", newline="") as fh:
        fh.write(updated)
    print(f"Updated release line to {tag} ({published}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
