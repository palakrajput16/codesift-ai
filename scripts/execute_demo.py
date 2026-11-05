
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "reports" / "generated_tests_demo.json"
OUTPUT_FILE = ROOT / "reports" / "demo_execution_results.json"


# Trusted, deliberately buggy implementation.
def is_adult(age):
    return age > 18


# Allowlist: only explicitly registered local functions can be executed.
TRUSTED_TARGETS = {
    "is_adult": is_adult,
}


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Generated test report not found: {INPUT_FILE}\n"
            "Run scripts/generate_demo.py first."
        )

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        suite = json.load(file)

    function_name = suite.get("function_name")
    target = TRUSTED_TARGETS.get(function_name)

    if target is None:
        raise ValueError(
            f"Function {function_name!r} is not in the trusted allowlist."
        )

    results = []

    for test in suite.get("tests", []):
        name = test["name"]
        args = test["args"]
        expected = test["expected"]

        try:
            actual = target(*args)
            passed = actual == expected

            result = {
                "name": name,
                "args": args,
                "expected": expected,
                "actual": actual,
                "status": "PASS" if passed else "FAIL",
                "error": None,
            }

        except Exception as exc:
            result = {
                "name": name,
                "args": args,
                "expected": expected,
                "actual": None,
                "status": "ERROR",
                "error": f"{type(exc).__name__}: {exc}",
            }

        results.append(result)

        print(
            f"[{result['status']}] {name} | "
            f"expected={expected!r}, actual={result['actual']!r}"
        )

    total = len(results)
    passed_count = sum(r["status"] == "PASS" for r in results)
    failed_count = sum(r["status"] == "FAIL" for r in results)
    error_count = sum(r["status"] == "ERROR" for r in results)

    report = {
        "project": "CodeSift",
        "stage": "milestone_3_demo_execution",
        "function_name": function_name,
        "total": total,
        "passed": passed_count,
        "failed": failed_count,
        "errors": error_count,
        "results": results,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print("\n--- Execution Summary ---")
    print(f"Total tests: {total}")
    print(f"Passed:      {passed_count}")
    print(f"Failed:      {failed_count}")
    print(f"Errors:      {error_count}")
    print(f"\nReport saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
