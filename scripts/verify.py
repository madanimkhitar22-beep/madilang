#!/usr/bin/env python3
"""One command, every gate.

    python scripts/verify.py

Exit code 0 means: the tree compiles, the ethics layer is alive, the gate
blocks, and the documented examples still behave. Run this before every
commit and at the start of every work session -- it is the cheapest way to
know where we stand.
"""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = sys.executable
results = []


def run(name, args, expect=0):
    proc = subprocess.run(
        args, cwd=str(ROOT), capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    ok = proc.returncode == expect
    results.append((name, ok, proc.returncode, expect, proc))
    return ok


TESTS = (
    "import sys; sys.path.insert(0, '.');"
    "import tests.test_ethics as t;"
    "ns = [n for n in dir(t) if n.startswith('test_')];"
    "[getattr(t, n)() for n in ns];"
    "print(len(ns), 'tests ok')"
)


def main():
    run("compileall", [PY, "-m", "compileall", "-q", "madilang"])
    run("unit tests", [PY, "-c", TESTS])
    run("check: passing example",
        [PY, "-m", "madilang", "check", "examples/auth.madi"], expect=0)
    run("check: README example",
        [PY, "-m", "madilang", "check", "examples/readme_example.madi"], expect=0)
    run("check: ethics gate blocks",
        [PY, "-m", "madilang", "check", "tests/fixtures/ethics_fail.madi"], expect=1)

    width = max(len(r[0]) for r in results)
    print()
    failed = 0
    for name, ok, code, expect, proc in results:
        print(("  PASS  " if ok else "  FAIL  ") + name.ljust(width)
              + "  exit=%s (expected %s)" % (code, expect))
        if not ok:
            failed += 1
            detail = (proc.stdout + proc.stderr).strip().splitlines()
            for line in detail[-6:]:
                print("        " + line)
    print("\n%d/%d gates green" % (len(results) - failed, len(results)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
