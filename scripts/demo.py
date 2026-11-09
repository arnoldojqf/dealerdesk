#!/usr/bin/env python3
"""Show TICKET-142 working: replay two fleet scenarios on a temp copy of the
fixture data and print the screens. Never touches data/ (decision D13)."""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True  # keep tests/ free of __pycache__
sys.path.insert(0, str(ROOT / "tests"))
import golden  # noqa: E402  (reuses read_sessions and FIXTURE)

SCENARIOS = ["fleet_quote_10000", "fleet_sell_view"]
RULE = "\n" + "~" * 62 + "\n"


def main():
    binary = ROOT / "dealerdesk"
    if not binary.exists():
        sys.exit("build first: make")
    for name in SCENARIOS:
        print("\n######## scenario %s ########" % name)
        with tempfile.TemporaryDirectory(prefix="dealerdesk-demo-") as tmp:
            shutil.copytree(golden.FIXTURE, Path(tmp) / "data")
            for i, script in enumerate(golden.read_sessions(name), 1):
                p = subprocess.run([str(binary)], cwd=tmp, input=script,
                                   capture_output=True, timeout=10)
                out = p.stdout.decode("latin-1").replace("\x1b[2J\x1b[H", RULE)
                print("---- run %d (exit %d) ----" % (i, p.returncode))
                print(out)
    print("\nDone. data/ was not touched; goldens are the real check: make test")


if __name__ == "__main__":
    main()
