#!/usr/bin/env python3
"""Checks that the committed agent setup is well formed (spec 003).

This proves the files exist and say what the spec requires, and that the
build hook behaves. It cannot prove what a model does with the commands.
Python standard library only.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
problems = []


def check(rid, ok, msg):
    print(("ok   " if ok else "FAIL ") + rid + (": " + msg if not ok else ""))
    if not ok:
        problems.append("%s: %s" % (rid, msg))


def front_matter(path):
    text = path.read_text()
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    return dict(l.split(":", 1) for l in m.group(1).splitlines() if ":" in l) if m else None


def make_targets():
    return set(re.findall(r"^([a-zA-Z][\w-]*):", (ROOT / "Makefile").read_text(), re.M))


def check_claude_md():
    p = ROOT / "CLAUDE.md"
    if not p.exists():
        return check("R1", False, "CLAUDE.md missing")
    text = p.read_text()
    targets = make_targets()
    problems_here = []
    required = ["make", "make warn", "make asan", "make test", "make test-asan",
                "make test-selfcheck", "git checkout -- data"]
    for r in required:
        if "`" + r + "`" not in text:
            problems_here.append("does not mention `%s`" % r)
    for t in re.findall(r"`make ([\w-]+)`", text):
        if t not in targets:
            problems_here.append("names make target '%s' that the Makefile lacks" % t)
    for tok in re.findall(r"`([^`\n]+)`", text):
        if re.search(r"[\s*<>{}]|NNN|http", tok) or tok.startswith(("-", "git ", "make", "./")):
            continue  # placeholders, commands, and run-this-binary examples
        if tok in ("dealerdesk", "dealerdesk-warn", "dealerdesk-asan"):
            continue  # build outputs, not files in the repo
        if re.fullmatch(r"\.\w+", tok) or tok in ("requirements.md", "design.md", "tasks.md"):
            continue  # a file extension, or a file name that exists inside every spec folder
        if "/" in tok or re.search(r"\.(md|py|c|h|json|sh|yml)$", tok):
            if not (ROOT / tok.rstrip("/")).exists():
                problems_here.append("names path '%s' that does not exist" % tok)
    for h in ["## Commands", "## Layout", "## Spec workflow", "## Hard rules"]:
        if h not in text:
            problems_here.append("missing section '%s'" % h)
    check("R1", not problems_here, "; ".join(problems_here))


def check_settings():
    p = ROOT / ".claude" / "settings.json"
    try:
        s = json.loads(p.read_text())
    except (OSError, ValueError) as e:
        for r in ("R2", "R3", "R4", "R5"):
            check(r, False, "settings.json unreadable: %s" % e)
        return
    perm = s.get("permissions", {})
    hooks = s.get("hooks", {}).get("PostToolUse", [])
    check("R2", all(k in perm for k in ("allow", "ask", "deny")) and bool(hooks),
          "needs permissions.allow/ask/deny and hooks.PostToolUse")
    need = {
        "R3": ("deny", ["Bash(git push:*)", "Bash(gh pr:*)", "Bash(gh repo:*)",
                        "Bash(git remote add:*)", "Bash(git remote set-url:*)",
                        "Bash(git remote remove:*)", "Bash(git remote rename:*)",
                        "Bash(rm -rf:*)", "Edit(data/**)", "Write(data/**)",
                        "Edit(tests/golden/**)", "Write(tests/golden/**)",
                        "Edit(tests/fixtures/**)", "Write(tests/fixtures/**)"]),
        "R4": ("ask", ["Bash(python3 tests/golden.py --update:*)", "Bash(git tag:*)",
                       "Bash(git checkout:*)", "Bash(git reset:*)", "Bash(gh api:*)"]),
        "R5": ("allow", ["Bash(make:*)", "Bash(python3 tests/golden.py)",
                         "Bash(python3 tests/golden.py --selfcheck)",
                         "Bash(git status:*)", "Bash(git diff:*)", "Bash(git log:*)",
                         "Bash(git show:*)", "Bash(git remote -v)", "Bash(git add:*)",
                         "Bash(git commit:*)", "Bash(gh run list:*)", "Bash(gh run view:*)"]),
    }
    for rid, (key, rules) in need.items():
        missing = [r for r in rules if r not in perm.get(key, [])]
        check(rid, not missing, "%s list lacks: %s" % (key, ", ".join(missing)))
    # --update must not be allowed by a broader allow rule's text
    wired = any("rebuild-on-c-edit.sh" in h.get("command", "")
                for e in hooks for h in e.get("hooks", []))
    check("R2 hook wiring", wired, "PostToolUse does not call rebuild-on-c-edit.sh")


def run_hook(project, file_path):
    hook = ROOT / ".claude" / "hooks" / "rebuild-on-c-edit.sh"
    payload = json.dumps({"tool_name": "Edit", "tool_input": {"file_path": str(file_path)}})
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(project))
    return subprocess.run(["bash", str(hook)], input=payload, text=True, env=env,
                          capture_output=True, timeout=120)


def check_hook():
    hook = ROOT / ".claude" / "hooks" / "rebuild-on-c-edit.sh"
    if not hook.exists():
        return check("R6", False, "hook script missing")
    with tempfile.TemporaryDirectory(prefix="dealerdesk-hook-") as tmp:
        tmp = Path(tmp)
        for f in list(ROOT.glob("*.c")) + list(ROOT.glob("*.h")) + [ROOT / "Makefile"]:
            shutil.copy(f, tmp)
        calc = tmp / "calc.c"
        original = calc.read_text()

        r = run_hook(tmp, calc)
        check("R6 clean build is silent", r.returncode == 0 and not (r.stdout + r.stderr).strip(),
              "rc=%s output=%r" % (r.returncode, (r.stdout + r.stderr)[:200]))

        calc.write_text(original + "\nint broken(void) { return ; \n")
        r = run_hook(tmp, calc)
        check("R6 compile error is reported", r.returncode == 2 and "error" in r.stderr,
              "rc=%s stderr=%r" % (r.returncode, r.stderr[:200]))

        calc.write_text(original + "\nstatic void warns(void) { int unused; }\n")
        r = run_hook(tmp, calc)
        check("R6 warning is reported", r.returncode == 2 and "warning" in r.stderr,
              "rc=%s stderr=%r" % (r.returncode, r.stderr[:200]))

        calc.write_text(original)
        (tmp / "Makefile").write_text("warn:\n\tfalse\n")  # would fail if make ran
        r = run_hook(tmp, tmp / "README.md")
        check("R6 non-C file does not run make", r.returncode == 0 and not (r.stdout + r.stderr).strip(),
              "rc=%s output=%r" % (r.returncode, (r.stdout + r.stderr)[:200]))

    # The edited file may live in another tree (a git worktree) than the one the
    # session was launched in. The hook must build the tree that holds the file.
    with tempfile.TemporaryDirectory(prefix="dealerdesk-hook-a-") as a, \
         tempfile.TemporaryDirectory(prefix="dealerdesk-hook-b-") as b:
        a, b = Path(a), Path(b)
        for d in (a, b):
            for f in list(ROOT.glob("*.c")) + list(ROOT.glob("*.h")) + [ROOT / "Makefile"]:
                shutil.copy(f, d)
        broken = b / "calc.c"
        broken.write_text(broken.read_text() + "\nint broken(void) { return ; \n")
        r = run_hook(a, broken)  # project dir a is clean, the edited file is in b
        check("R6 builds the tree that holds the edited file",
              r.returncode == 2 and "error" in r.stderr,
              "rc=%s stderr=%r" % (r.returncode, r.stderr[:200]))


def check_commands_and_agent():
    for name in ("spec", "implement", "verify"):
        p = ROOT / ".claude" / "commands" / (name + ".md")
        fm = front_matter(p) if p.exists() else None
        check("R7 /" + name, bool(fm) and "description" in fm and "argument-hint" in fm,
              "%s missing or lacks description/argument-hint front matter" % p.relative_to(ROOT))
    p = ROOT / ".claude" / "agents" / "spec-reviewer.md"
    fm = front_matter(p) if p.exists() else None
    check("R8 spec-reviewer", bool(fm) and all(k in fm for k in ("name", "description", "tools")),
          "agent file missing or lacks name/description/tools")
    if fm and "tools" in fm:
        tools = fm["tools"]
        check("R8 reviewer is read-only", "Edit" not in tools and "Write" not in tools,
              "reviewer must not have Edit or Write: %s" % tools.strip())


def main():
    check_claude_md()
    check_settings()
    check_hook()
    check_commands_and_agent()
    if problems:
        print("\n%d problem(s):" % len(problems))
        for p in problems:
            print("  -", p)
        return 1
    print("\nagent setup ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
