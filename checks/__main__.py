"""Run: python -m checks N   (checks weeks 1 to N, then Git)"""
import importlib
import sys

from checks.util import sh


def git_checks():
    out = []
    code, log = sh(["git", "log", "--oneline"])
    out.append(("Git: at least one commit", code == 0 and bool(log), "run git add . and git commit"))
    code, remotes = sh(["git", "remote"])
    out.append(("Git: remote 'origin' is set", "origin" in remotes, "git remote add origin <your repo address>"))
    _, tracked = sh(["git", "ls-files"])
    bad = [p for p in tracked.split() if p == ".env" or p.startswith(("venv/", "data/"))]
    out.append(("Git: no venv, data or .env tracked", not bad, "git rm -r --cached venv data, add them to .gitignore"))
    _, status = sh(["git", "status", "--porcelain"])
    out.append(("Git: everything is committed", status == "", "commit your last changes"))
    c1, head = sh(["git", "rev-parse", "HEAD"])
    c2, up = sh(["git", "rev-parse", "@{u}"])
    out.append(("Git: latest commit is pushed to GitHub", c1 == 0 and c2 == 0 and head == up, "git push"))
    return out


def main():
    upto = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    results = []
    for week in range(1, upto + 1):
        print(f"== Week {week} ==")
        mod = importlib.import_module(f"checks.week{week}")
        for name, ok, hint in mod.run():
            if ok is None:
                print("SKIP  " + name)
                continue
            results.append(ok)
            print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else f"   -> {hint}"))
    print("== Git ==")
    for name, ok, hint in git_checks():
        results.append(ok)
        print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else f"   -> {hint}"))
    print(f"RESULT: {sum(results)}/{len(results)} checks passed")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
