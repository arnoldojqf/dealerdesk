#!/usr/bin/env python3
"""Golden-master harness for DealerDesk (spec 002).

Runs scripted keystrokes through the binary in a temp copy of the fixture
data and compares stdout, exit code and changed .dat files with the approved
files in tests/golden/<scenario>/. Characterisation only: it records what the
program does today, bugs included.

    python3 tests/golden.py [--bin PATH] [--update] [--selfcheck] [NAME ...]
"""
import argparse
import datetime
import difflib
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "tests" / "fixtures" / "data"
SCENARIOS = ROOT / "tests" / "scenarios"
GOLDEN = ROOT / "tests" / "golden"
DAT_FILES = ["stock.dat", "customers.dat", "invoices.dat", "next_ids.dat"]


def today():
    return datetime.date.today().isoformat()


def normalise(data, day):
    """bytes -> text. latin-1 is lossless; mask the date and the ESC byte."""
    return data.decode("latin-1").replace(day, "<TODAY>").replace("\x1b", "<ESC>")


def read_sessions(name):
    """Scenario file -> list of stdin scripts, one per program run.

    '#' lines are comments; a blank line is the ENTER key; a line of '---'
    starts a new run of the program on the same data (to see what a reload
    does, e.g. bug B2)."""
    sessions, cur = [], []
    for l in (SCENARIOS / (name + ".txt")).read_text().splitlines():
        if l == "---":
            sessions.append(cur)
            cur = []
        elif not l.startswith("#"):
            cur.append(l)
    sessions.append(cur)
    return ["".join(l + "\n" for l in s).encode() for s in sessions]


def run_once(binary, name, timeout, day):
    """Run one scenario in a temp dir. Returns a result dict."""
    with tempfile.TemporaryDirectory(prefix="dealerdesk-test-") as tmp:
        shutil.copytree(FIXTURE, Path(tmp) / "data")
        outs, codes, errs = [], [], ""
        for script in read_sessions(name):
            try:
                p = subprocess.run([str(binary)], cwd=tmp, input=script,
                                   capture_output=True, timeout=timeout)
            except subprocess.TimeoutExpired:
                return {"timed_out": True, "files": {}, "stderr": ""}
            outs.append(normalise(p.stdout, day))
            codes.append(p.returncode)
            errs += p.stderr.decode("latin-1")
        if len(outs) == 1:
            stdout = outs[0]
        else:
            stdout = "".join("=== run %d ===\n%s\n" % (i + 1, o)
                             for i, o in enumerate(outs))
        files = {
            "stdout.txt": stdout,
            "exit_code.txt": "".join("%d\n" % c for c in codes),
        }
        for dat in DAT_FILES:
            got = normalise((Path(tmp) / "data" / dat).read_bytes(), day)
            want = normalise((FIXTURE / dat).read_bytes(), day)
            if got != want:  # only changed files are stored (A3)
                files["data/" + dat] = got
        return {"timed_out": False, "files": files, "stderr": errs}


def run_scenario(binary, name, timeout):
    """Run, re-running once if midnight passed during the run (R3)."""
    for _ in range(2):
        before = today()
        result = run_once(binary, name, timeout, before)
        if today() == before:
            return result
    raise SystemExit("scenario %s kept straddling midnight" % name)


def read_golden(name):
    base = GOLDEN / name
    if not base.is_dir():
        return None
    return {str(p.relative_to(base)): p.read_text(encoding="latin-1")
            for p in sorted(base.rglob("*")) if p.is_file()}


def write_golden(name, files):
    base = GOLDEN / name
    if base.exists():
        shutil.rmtree(base)
    for rel, text in files.items():
        path = base / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="latin-1")


def diff(name, want, got):
    out = []
    for rel in sorted(set(want) | set(got)):
        if want.get(rel) != got.get(rel):
            out += difflib.unified_diff(
                want.get(rel, "").splitlines(keepends=True),
                got.get(rel, "").splitlines(keepends=True),
                fromfile="golden/%s/%s" % (name, rel),
                tofile="actual/%s/%s" % (name, rel))
            if rel not in want or rel not in got:
                out.append("(%s only in %s)\n" % (
                    rel, "actual" if rel not in want else "golden"))
    return "".join(out)


def hash_data():
    d = ROOT / "data"
    return hashlib.sha256(b"".join(
        (d / f).read_bytes() for f in DAT_FILES if (d / f).exists())).hexdigest()


def run_suite(binary, names, timeout, update=False, fail_on_stderr=False,
              quiet=False):
    """Returns the list of failing scenario names."""
    failures = []
    for name in names:
        res = run_scenario(binary, name, timeout)
        if res["timed_out"]:
            print("FAIL %s: timed out after %ss" % (name, timeout))
            failures.append(name)
            continue
        if res["stderr"]:  # the program never writes to stderr; ASan/UBSan do
            print("FAIL %s: wrote to stderr:\n%s" % (name, res["stderr"]))
            failures.append(name)
            continue
        if update:
            write_golden(name, res["files"])
            print("UPDATED %s (%s)" % (name, ", ".join(sorted(res["files"]))))
            continue
        want = read_golden(name)
        if want is None:
            print("FAIL %s: no approved files; review the output, then run "
                  "with --update" % name)
            failures.append(name)
        elif want != res["files"]:
            print("FAIL %s" % name)
            if not quiet:
                sys.stdout.write(diff(name, want, res["files"]))
            failures.append(name)
        elif not quiet:
            print("PASS %s" % name)
    return failures


def selfcheck(timeout):
    """Proves the suite itself works (R3, R4, R5, R6, R14, R15)."""
    global GOLDEN
    names = all_names()
    cc = os.environ.get("CC", "gcc")
    results = []

    def verdict(label, ok, detail=""):
        print("selfcheck %-44s %s %s" % (label, "ok" if ok else "FAILED", detail))
        results.append(ok)

    real_golden = GOLDEN
    with tempfile.TemporaryDirectory(prefix="dealerdesk-selfcheck-") as tmp:
        tmp = Path(tmp)
        for src in list(ROOT.glob("*.c")) + list(ROOT.glob("*.h")):
            shutil.copy(src, tmp)
        sources = [str(c) for c in tmp.glob("*.c")]
        clean = tmp / "dealerdesk-clean"
        subprocess.run([cc, "-o", str(clean)] + sources + ["-lm"], check=True)

        # R14: a changed trade discount is noticed
        calc = (tmp / "calc.c").read_text()
        assert "list * 0.10" in calc, "mutation target moved"
        (tmp / "calc.c").write_text(calc.replace("list * 0.10", "list * 0.11"))
        mutant = tmp / "dealerdesk-mutant"
        subprocess.run([cc, "-o", str(mutant)] + sources + ["-lm"], check=True)
        failed = run_suite(mutant, names, timeout, quiet=True)
        verdict("R14 mutation (trade 10%->11%) fails scenarios", bool(failed), ", ".join(failed))

        # R6: a hanging binary times out
        hang = tmp / "dealerdesk-hang"
        hang.write_text("#!/bin/sh\nsleep 30\n")
        hang.chmod(0o755)
        verdict("R6  hanging binary times out",
                run_suite(hang, names[:1], 1, quiet=True) == names[:1])

        # R3: two consecutive runs give identical captured output
        a = run_scenario(clean, "sell_retail_view", timeout)
        b = run_scenario(clean, "sell_retail_view", timeout)
        verdict("R3  two runs are identical (date masked)", a == b and "<TODAY>" in a["files"]["stdout.txt"])

        # R4: a tampered golden fails; R5: a missing golden fails with guidance
        tampered = tmp / "golden-tampered"
        shutil.copytree(real_golden, tampered)
        f = tampered / "stock_list" / "stdout.txt"
        f.write_text(f.read_text().replace("9 vehicle(s)", "8 vehicle(s)"))
        GOLDEN = tampered
        verdict("R4  tampered golden fails", run_suite(clean, ["stock_list"], timeout, quiet=True) == ["stock_list"])
        GOLDEN = tmp / "golden-empty"
        GOLDEN.mkdir()
        verdict("R5  missing golden fails", run_suite(clean, ["stock_list"], timeout, quiet=True) == ["stock_list"])
        GOLDEN = real_golden

        # R5: --update is refused when CI is set, and changes nothing
        before = sorted((p.name, p.read_bytes()) for p in (real_golden / "stock_list").rglob("*") if p.is_file())
        r = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--update", "stock_list"],
                           env=dict(os.environ, CI="1"), capture_output=True, text=True)
        after = sorted((p.name, p.read_bytes()) for p in (real_golden / "stock_list").rglob("*") if p.is_file())
        verdict("R5  --update refused under CI, golden unchanged",
                r.returncode == 2 and "refusing" in r.stdout and before == after)

        # R2/R15: anything on stderr fails, even if stdout is identical
        noisy = tmp / "dealerdesk-noisy"
        noisy.write_text('#!/bin/sh\necho "ERROR: AddressSanitizer: fake" >&2\nexec "%s"\n' % clean)
        noisy.chmod(0o755)
        quiet_wrap = tmp / "dealerdesk-quiet"
        quiet_wrap.write_text('#!/bin/sh\nexec "%s"\n' % clean)
        quiet_wrap.chmod(0o755)
        verdict("R2  stderr output fails the scenario",
                run_suite(noisy, ["stock_list"], timeout, quiet=True) == ["stock_list"]
                and run_suite(quiet_wrap, ["stock_list"], timeout, quiet=True) == [])
    GOLDEN = real_golden
    print("selfcheck:", "ok" if all(results) else "FAILED")
    return 0 if all(results) else 1


def all_names():
    return sorted(p.stem for p in SCENARIOS.glob("*.txt"))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("names", nargs="*", help="scenario names (default: all)")
    ap.add_argument("--bin", default=str(ROOT / "dealerdesk"))
    ap.add_argument("--update", action="store_true",
                    help="rewrite approved files (refused when CI is set)")
    ap.add_argument("--selfcheck", action="store_true")
    ap.add_argument("--fail-on-stderr", action="store_true",
                    help="accepted for compatibility; stderr output always fails now")
    ap.add_argument("--timeout", type=int, default=10)
    a = ap.parse_args()

    if a.selfcheck:
        return selfcheck(a.timeout)
    if a.update and os.environ.get("CI"):
        print("refusing --update: CI is set (goldens are approved by a human)")
        return 2
    known = all_names()
    bad = [n for n in a.names if n not in known]
    if bad:
        print("unknown scenario(s):", ", ".join(bad))
        return 2
    names = a.names or known

    before = hash_data()
    failures = run_suite(Path(a.bin).resolve(), names, a.timeout, a.update,
                         a.fail_on_stderr)
    if hash_data() != before:
        print("FAIL: the repository's data/ changed during the run (R1)")
        return 1
    if not a.update:
        print("\n%d passed, %d failed" % (len(names) - len(failures), len(failures)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
