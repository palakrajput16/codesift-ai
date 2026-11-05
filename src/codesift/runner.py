import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from codesift.benchmark import BENCHMARK
from codesift.metrics import summarise_results


REPORTS_DIR = PROJECT_ROOT / "reports"


def evaluate_function(function, test_case):
    """Execute a function on one test input and compare its output."""

    try:
        actual = function(*test_case.args)

        return {
            "status": (
                "passed"
                if actual == test_case.expected
                else "failed"
            ),
            "actual": actual,
            "expected": test_case.expected,
            "error": None,
        }

    except Exception as exc:
        return {
            "status": "error",
            "actual": None,
            "expected": test_case.expected,
            "error": f"{type(exc).__name__}: {exc}",
        }


def evaluate_bug_case(case):
    """Evaluate buggy and fixed implementations on the same tests."""

    test_results = []

    for test_case in case.tests:
        buggy_result = evaluate_function(
            case.buggy_function, test_case
        )

        fixed_result = evaluate_function(
            case.fixed_function, test_case
        )

        test_results.append({
            "test_name": test_case.name,
            "buggy_status": buggy_result["status"],
            "buggy_actual": buggy_result["actual"],
            "buggy_error": buggy_result["error"],
            "fixed_status": fixed_result["status"],
            "fixed_actual": fixed_result["actual"],
            "fixed_error": fixed_result["error"],
            "expected": test_case.expected,
        })

    buggy_caught = any(
        test["buggy_status"] != "passed"
        for test in test_results
    )

    fixed_passed_all = all(
        test["fixed_status"] == "passed"
        for test in test_results
    )

    return {
        "bug_id": case.bug_id,
        "category": case.category,
        "description": case.description,
        "buggy_caught": buggy_caught,
        "fixed_passed_all": fixed_passed_all,
        "bug_detected": buggy_caught and fixed_passed_all,
        "tests": test_results,
    }


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    results = [
        evaluate_bug_case(case)
        for case in BENCHMARK
    ]

    report = {
        "project": "CodeSift",
        "benchmark_version": "0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "results": results,
        "summary": summarise_results(results),
    }

    report_path = REPORTS_DIR / "benchmark_report.json"

    report_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(report["summary"], indent=2))
    print("\nIndividual bug results:")

    for result in results:
        status = "DETECTED" if result["bug_detected"] else "CHECK"
        print(f'{result["bug_id"]}: {status} — {result["description"]}')

    print(f"\nFull report saved to: {report_path}")


if __name__ == "__main__":
    main()