"""Pre-commit hook: verify tests are staged when production code changes.

Rule: if any staged file lives under src/app/, at least one staged file
must live under src/tests/. This is the codifiable part of the work-unit
commit discipline — everything else (triangulation, refactor timing, RED
order) requires human judgment.
"""

import subprocess
import sys


def get_staged_files() -> list[str]:
    """Return list of staged file paths (empty if no changes staged)."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True,
        text=True,
    )
    return [f for f in result.stdout.strip().split("\n") if f]


def check(verbose: bool = False) -> int:
    staged = get_staged_files()

    if not staged:
        if verbose:
            print("Nothing staged — skipping test-coverage check.")
        return 0

    prod_files = [f for f in staged if f.startswith("src/app/")]
    test_files = [f for f in staged if f.startswith("src/tests/")]

    if not prod_files:
        if verbose:
            print("No production code staged — skipping test-coverage check.")
        return 0

    if not test_files:
        print("=" * 60)
        print("  WORK-UNIT COMMIT VIOLATION")
        print("=" * 60)
        print()
        print("  You changed production code but no tests are staged:")
        for f in prod_files:
            print(f"    • {f}")
        print()
        print("  TDD rule: every production-code change must ship with its tests.")
        print("  Stage the test file(s) and try again, or run:")
        print()
        print("    git commit --no-verify  (if you know what you're doing)")
        print()
        return 1

    if verbose:
        print("Production + tests staged — work-unit check passed.")
    return 0


if __name__ == "__main__":
    verbose = "--quiet" not in sys.argv
    sys.exit(check(verbose=verbose))
