#!/usr/bin/env python3
r"""Public-repository hygiene check (format only).

Looks at tracked files and reports:
  error   - files that must not be tracked in a public repo
            (state.md at the root, CLAUDE.local.md, .claude/, _private/, *.private.*, .env and .env.* except .env.example)
  error   - absolute paths into a user's home directory (C:\Users\<name>, /Users/<name>, /home/<name>)
  warning - internal project-number tokens (the letter P, a hyphen, three digits)

It matches fixed formats only; it does not judge what a file is about.
Files can be excluded with `.concordia-allow` (one glob per line, `#` comments).

Usage: python hygiene.py [--root DIR] [--strict]
  --strict  treat warnings as errors
Exit code 1 if any error was found.
"""
import argparse
import fnmatch
import os
import re
import subprocess
import sys

FORBIDDEN = [
    (re.compile(r"^state\.md$"), "local state file"),
    (re.compile(r"(^|/)CLAUDE\.local\.md$"), "local agent notes"),
    (re.compile(r"(^|/)\.claude/"), "local agent settings"),
    (re.compile(r"(^|/)_private/"), "private folder"),
    (re.compile(r"(^|/)[^/]*\.private\.[^/]+$"), "private file"),
    (re.compile(r"(^|/)\.env(\.(?!example$)[^/]+)?$"), "environment file"),
]
HOME_PATH = re.compile(
    r"[A-Za-z]:[\\/]{1,2}Users[\\/]{1,2}(?!(?:Public|Default|All Users)\b)[A-Za-z0-9._-]+"
    r"|(?<![\w.])/(?:Users|home)/(?!runner\b|user\b|username\b|you\b)[A-Za-z0-9._-]+"
)
PROJECT_ID = re.compile(r"\bP-\d{3}(?:-[A-Z])?\b")
MAX_BYTES = 1_000_000


def tracked(root):
    out = subprocess.run(["git", "ls-files", "-z"], cwd=root, capture_output=True, check=True).stdout
    return [p for p in out.decode("utf-8", "replace").split("\0") if p]


def allow_globs(root):
    path = os.path.join(root, ".concordia-allow")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return [l.strip() for l in fh if l.strip() and not l.startswith("#")]


def allowed(path, globs):
    return any(fnmatch.fnmatch(path, g) for g in globs)


def text(root, path):
    full = os.path.join(root, path)
    try:
        if os.path.getsize(full) > MAX_BYTES:
            return None
        with open(full, "rb") as fh:
            data = fh.read()
    except OSError:
        return None
    if b"\0" in data:
        return None
    return data.decode("utf-8", "replace")


def check(root):
    """Return a list of (level, path, line, message)."""
    found = []
    globs = allow_globs(root)
    for path in tracked(root):
        if allowed(path, globs):
            continue
        for pattern, what in FORBIDDEN:
            if pattern.search(path):
                found.append(("error", path, 0, "tracked %s should not be in a public repository" % what))
                break
        body = text(root, path)
        if body is None:
            continue
        for n, line in enumerate(body.splitlines(), 1):
            if HOME_PATH.search(line):
                found.append(("error", path, n, "absolute home-directory path"))
            if PROJECT_ID.search(line):
                found.append(("warning", path, n, "internal project-number token"))
    return found


def main(argv=None):
    ap = argparse.ArgumentParser(description="Public-repository hygiene check (format only).")
    ap.add_argument("--root", default=".")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args(argv)
    found = check(a.root)
    gha = os.environ.get("GITHUB_ACTIONS") == "true"
    errors = 0
    for level, path, line, msg in found:
        if a.strict:
            level = "error"
        errors += level == "error"
        if gha:
            loc = "file=%s" % path + (",line=%d" % line if line else "")
            print("::%s %s::%s" % (level, loc, msg))
        else:
            print("%s: %s%s: %s" % (level, path, ":%d" % line if line else "", msg))
    print("hygiene: %d error(s), %d warning(s)" % (errors, len(found) - errors))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
