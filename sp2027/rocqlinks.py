#!/usr/bin/env python3
"""Refresh the line numbers in rocqlinks.tex from a checkout of SigmaProtocol.

Every entry of rocqlinks.tex has the form

    \\rocqdef{<rocq name>}{<repo-relative path>}{<line>}

This script looks up the line where <rocq name> is defined in <path> (a
Definition/Lemma/Theorem/... or an inductive constructor `| name`) and
rewrites <line>. Run it after updating the anonymous snapshot:

    python3 rocqlinks.py ../../SigmaProtocol

It exits non-zero and leaves the file untouched if a name is not found.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "rocqlinks.tex")
ENTRY = re.compile(r"\\rocqdef\{([^}]*)\}\{([^}]*)\}\{(\d*)\}")
KW = (r"(?:Theorem|Lemma|Definition|Fixpoint|Inductive|Record|Corollary|Instance|"
      r"Class|Module|Proposition|Fact|Remark|Example|Let|Section)")


def find_line(path, name):
    if not path.endswith(".v"):
        return None  # plain file or directory: no line anchor
    ident = re.escape(name)
    decl = re.compile(r"\s*(?:#\[[^\]]*\]\s*)?(?:(?:Global|Local|Polymorphic|Program)\s+)*"
                      + KW + r"\s+" + ident + r"(?![A-Za-z0-9_'])")
    ctor = re.compile(r"\s*\|\s*" + ident + r"(?![A-Za-z0-9_'])")
    with open(path, encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    for pat in (decl, ctor):
        for i, line in enumerate(lines, 1):
            if pat.match(line):
                return i
    raise LookupError(f"{name} not found in {path}")


def main():
    repo = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "SigmaProtocol")
    text = open(TEX, encoding="utf-8").read()
    errors = []

    def fix(m):
        name, path, _ = m.groups()
        full = os.path.join(repo, path)
        if not os.path.exists(full):
            errors.append(f"missing file {path}")
            return m.group(0)
        try:
            line = find_line(full, name.replace("\\_", "_"))
        except LookupError as e:
            errors.append(str(e))
            return m.group(0)
        return "\\rocqdef{%s}{%s}{%s}" % (name, path, "" if line is None else line)

    new = ENTRY.sub(fix, text)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(1)
    if new != text:
        open(TEX, "w", encoding="utf-8").write(new)
        print("rocqlinks.tex updated")
    else:
        print("rocqlinks.tex already up to date")


if __name__ == "__main__":
    main()
