#!/usr/bin/env python3
"""Validate repository logs and protocol references.

Checks performed:
- Per-issue log filenames: must match `<slug>-YYYY-MM-DD.md` (lower-case, hyphens only in slug)
- No emoji characters present in filenames or file contents for files under Documentation/logs/ and Documentation/Protocols/
- Each per-issue log referenced in `Documentation/Protocols/master_log.md` (simple substring match)

Exit code 0 on success, non-zero on failures.
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = ROOT / "Documentation" / "logs"
MASTER_LOG = ROOT / "Documentation" / "Protocols" / "master_log.md"

# Filename pattern: slug-YYYY-MM-DD.md where slug is [a-z0-9-]+
FNAME_RE = re.compile(r"^([a-z0-9\-]+)-([0-9]{4})-([0-9]{2})-([0-9]{2})\.md$")

# Simple emoji range detection regex (covers common emoji blocks)
EMOJI_RE = re.compile(
    "[\U0001F300-\U0001F5FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF]"
)

def find_log_files():
    if not LOGS_DIR.exists():
        return []
    # Only consider per-issue log files that match the expected filename pattern.
    files = []
    for p in LOGS_DIR.iterdir():
        if not p.is_file() or p.suffix != ".md":
            continue
        if FNAME_RE.match(p.name):
            files.append(p)
    return files

def check_filenames(files):
    errors = []
    for p in files:
        name = p.name
        m = FNAME_RE.match(name)
        if not m:
            errors.append(f"Bad filename: {name} (must be: <slug>-YYYY-MM-DD.md with lower-case slug and hyphens)")
    return errors

def check_for_emoji_in_file(p: Path):
    try:
        text = p.read_text(encoding="utf-8")
    except Exception as e:
        return [f"Could not read {p}: {e}"]
    if EMOJI_RE.search(text):
        return [f"Emoji or disallowed pictograph found in {p}"]
    return []

def check_master_log_references(files):
    errors = []
    if not MASTER_LOG.exists():
        return [f"Missing master_log.md at {MASTER_LOG}"]
    master_text = MASTER_LOG.read_text(encoding="utf-8")
    for p in files:
        if p.name not in master_text:
            errors.append(f"{p.name} not referenced in {MASTER_LOG}")
    return errors

def main():
    files = find_log_files()
    if not files:
        print("Warning: no log files found in Documentation/logs/ (skipping filename checks)")
    errs = []
    errs.extend(check_filenames(files))
    for p in files:
        errs.extend(check_for_emoji_in_file(p))
    # also check protocol files for emoji
    protocols_dir = ROOT / "Documentation" / "Protocols"
    if protocols_dir.exists():
        for p in protocols_dir.iterdir():
            if p.is_file() and p.suffix == ".md":
                errs.extend(check_for_emoji_in_file(p))
    errs.extend(check_master_log_references(files))

    if errs:
        print("Validation failed:\n" + "\n".join(errs))
        sys.exit(2)
    print("Validation passed: logs and protocols look good.")

if __name__ == '__main__':
    main()
