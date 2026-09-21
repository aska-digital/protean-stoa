#!/usr/bin/env python3
"""check-internal-names.py - leak gate for private identifiers.

Two independent detectors:

  D1 token digests  - every alphanumeric token in every scanned file is
                      lower-cased and hashed; a digest that appears in
                      gates/internal-names.blocklist is a leak. The blocklist
                      ships digests only, so this file never carries a private
                      name.
  D2 path shapes    - regexes that match machine-specific absolute paths and
                      private knowledge-base markers without spelling a single
                      example of one.

Usage: python3 gates/check-internal-names.py [--diff-only] [path/to/repo]

  --diff-only  scan only files changed on this branch vs origin/main
               (git merge-base HEAD origin/main, then git diff --name-only).
               For PR checks: pre-existing findings elsewhere in the tree do
               not fail the PR. Without the flag the full tree is scanned.
Exit: 0 clean; 1 leak found.
"""
import hashlib
import os
import re
import subprocess
import sys

TOKEN_RE = re.compile(r"[A-Za-z0-9]+")

# Written so that no literal instance of a blocked path shape appears here.
PATH_RES = [
    re.compile(r"/" + r"(?:Users|home|Volumes)" + r"/"),
    re.compile(r"~/\.(?:hermes|config|local|cache|ssh)"),
    re.compile(r"(?:^|[^A-Za-z0-9_-])" + r"team[-_]skills" + r"(?:[^A-Za-z0-9_-]|$)"),
    re.compile(r"cache" + r"/" + r"delegation"),
    re.compile(r"(?:^|[^A-Za-z0-9_])" + r"profiles" + r"/"),
    re.compile(r"Documents" + r"/" + r"ai work"),
]

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv"}
SKIP_EXT = (".pyc", ".so", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip",
            ".woff", ".woff2", ".ttf", ".ico")
SELF_EXCLUDE = {"gates/check-internal-names.py", "gates/internal-names.blocklist",
                # Allowlist documents pre-existing public role identifiers in
                # plain text, so it must never be scanned itself.
                "gates/internal-names.allowlist"}


def load_blocklist(repo):
    path = os.path.join(repo, "gates", "internal-names.blocklist")
    digests = set()
    if not os.path.exists(path):
        raise SystemExit("gate error: gates/internal-names.blocklist missing")
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                digests.add(line)
    return digests


def load_allowlist(repo):
    # Digest-based exclusion only: parse the public role identifiers named
    # in comments in gates/internal-names.allowlist, hash each lowercased
    # name with SHA256, and return the digest set. Never compares plain-text
    # names against scanned content. Fail closed on missing/unparseable file.
    import hashlib as _hl
    path = os.path.join(repo, "gates", "internal-names.allowlist")
    if not os.path.exists(path):
        raise SystemExit("gate error: gates/internal-names.allowlist missing")
    name_re = re.compile(r"^[A-Za-z0-9_-]+$")
    names = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            s = line.strip()
            # Only identifier-list comment lines: '#' followed by
            # comma-separated tokens (e.g. '#   proteus, mozi, ...').
            if not s.startswith("#"):
                continue
            body = s.lstrip("#").strip()
            if "," not in body:
                continue
            if not re.fullmatch(r"[A-Za-z0-9_, \t-]+", body):
                continue
            for part in body.split(","):
                token = part.strip()
                if token and name_re.fullmatch(token):
                    names.append(token.lower())
    if not names:
        raise SystemExit(
            "gate error: gates/internal-names.allowlist unparseable "
            "(no identifiers found)")
    return {_hl.sha256(n.encode("utf-8")).hexdigest() for n in names}


def git_changed_files(repo):
    """Repo-relative paths changed on this branch vs origin/main."""
    def run(*args):
        try:
            proc = subprocess.run(["git"] + list(args), cwd=repo,
                                  capture_output=True, text=True, check=True)
        except (OSError, subprocess.CalledProcessError) as exc:
            raise SystemExit("gate error: --diff-only needs origin/main "
                             "(git %s failed: %s)" % (" ".join(args), exc))
        return proc.stdout
    base = run("merge-base", "HEAD", "origin/main").strip()
    if not base:
        raise SystemExit("gate error: --diff-only: empty merge-base with origin/main")
    out = run("diff", "--name-only", base, "HEAD")
    return [line.strip() for line in out.splitlines() if line.strip()]


def scan(repo, digests, allowlist=None, only=None):
    findings = []
    scanned = 0
    allowlist = allowlist or set()
    only_set = set(only) if only is not None else None
    for root, dirs, files in os.walk(repo):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            if name.endswith(SKIP_EXT):
                continue
            abspath = os.path.join(root, name)
            rel = os.path.relpath(abspath, repo).replace(os.sep, "/")
            if rel in SELF_EXCLUDE or not os.path.isfile(abspath):
                continue
            if only_set is not None and rel not in only_set:
                continue
            scanned += 1
            try:
                with open(abspath, encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
            except OSError:
                continue
            for lineno, line in enumerate(text.splitlines(), 1):
                for match in TOKEN_RE.finditer(line):
                    digest = hashlib.sha256(
                        match.group(0).lower().encode("utf-8")).hexdigest()
                    if digest in digests and digest not in allowlist:
                        findings.append((rel, lineno, "token-digest"))
                for rx in PATH_RES:
                    if rx.search(line):
                        findings.append((rel, lineno, "private-path"))
    return scanned, findings


def main():
    args = [a for a in sys.argv[1:] if a != "--diff-only"]
    diff_only = len(args) != len(sys.argv[1:])
    repo = os.path.abspath(args[0] if args else ".")
    digests = load_blocklist(repo)
    allowlist = load_allowlist(repo)
    only = None
    if diff_only:
        only = git_changed_files(repo)
        print("mode: diff-only (" + str(len(only)) + " changed file(s) vs origin/main)")
    else:
        print("mode: full-tree")
    scanned, findings = scan(repo, digests, allowlist, only)
    if findings:
        print("LEAK: " + str(len(findings)) + " finding(s)")
        for rel, lineno, kind in findings[:40]:
            print("  " + rel + ":" + str(lineno) + " [" + kind + "]")
        print("files scanned: " + str(scanned))
        return 1
    print("clean: " + str(scanned) + " files scanned, 0 findings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
