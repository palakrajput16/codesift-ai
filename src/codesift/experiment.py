
import math
from typing import Any, Callable

from codesift.benchmark import BugCase, TestCase
from codesift.generation.schema import GeneratedTestSuite


def values_match(actual: Any, expected: Any) -> bool:
    """Compare values while handling floats and strict types."""

    if isinstance(actual, bool) or isinstance(expected, bool):
        return type(actual) is type(expected) and actual == expected

    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        return math.isclose(
            actual,
            expected,
            rel_tol=1e-9,
            abs_tol=1e-9,
        )

    if type(actual) is not type(expected):
        return False

    if isinstance(actual, list):
        return (
            len(actual) == len(expected)
            and all(
                values_match(a, e)
                for a, e in zip(actual, expected)
            )
        )

    if isinstance(actual, tuple):
        return (
            len(actual) == len(expected)
            and all(
                values_match(a, e)
                for a, e in zip(actual, expected)
            )
        )

    if isinstance(actual, dict):
        return (
            actual.keys() == expected.keys()
            and all(
                values_match(actual[key], expected[key])
                for key in actual
            )
        )

    return actual == expected


def execute_test_suite(
    suite: GeneratedTestSuite,
    target: Callable,
) -> list[dict[str, Any]]:
    results = []

    for test in suite.tests:
        try:
            actual = target(*test.args)
            passed = values_match(actual, test.expected)

            results.append({
                "name": test.name,
                "args": test.args,
                "expected": test.expected,
                "actual": actual,
                "status": "PASS" if passed else "FAIL",
                "error": None,
            })

        except Exception as exc:
            results.append({
                "name": test.name,
                "args": test.args,
                "expected": test.expected,
                "actual": None,
                "status": "ERROR",
                "error": f"{type(exc).__name__}: {exc}",
            })

    return results


def evaluate_generated_suite(
    suite: GeneratedTestSuite,
    case: BugCase,
) -> dict[str, Any]:
    buggy_results = execute_test_suite(
        suite,
        case.buggy_function,
    )

    fixed_results = execute_test_suite(
        suite,
        case.fixed_function,
    )

    detected_tests = [
        buggy
        for buggy, fixed in zip(buggy_results, fixed_results)
        if buggy["status"] in ("FAIL", "ERROR")
        and fixed["status"] == "PASS"
    ]

    false_positive_tests = [
        result
        for result in fixed_results
        if result["status"] in ("FAIL", "ERROR")
    ]

    total_tests = len(suite.tests)

    return {
        "bug_id": case.bug_id,
        "function_name": suite.function_name,
        "total_generated_tests": total_tests,
        "bug_detected": len(detected_tests) > 0,
        "detected_test_count": len(detected_tests),
        "false_positive_count": len(false_positive_tests),
        "buggy_results": buggy_results,
        "fixed_results": fixed_results,
        "detected_tests": detected_tests,
        "false_positive_tests": false_positive_tests,
    }


def evaluate_hidden_tests(
    target: Callable,
    hidden_tests: list[TestCase],
) -> list[dict[str, Any]]:
    results = []

    for test in hidden_tests:
        try:
            actual = target(*test.args)
            passed = values_match(actual, test.expected)

            results.append({
                "name": test.name,
                "status": "PASS" if passed else "FAIL",
                "expected": test.expected,
                "actual": actual,
                "error": None,
            })

        except Exception as exc:
            results.append({
                "name": test.name,
                "status": "ERROR",
                "expected": test.expected,
                "actual": None,
                "error": f"{type(exc).__name__}: {exc}",
            })

    return results
