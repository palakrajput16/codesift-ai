from collections import defaultdict


def summarise_results(case_results: list[dict]) -> dict:
    total_cases = len(case_results)

    detected_cases = sum(
        result["bug_detected"]
        for result in case_results
    )

    validated_cases = sum(
        result["fixed_passed_all"]
        for result in case_results
    )

    total_tests = sum(
        len(result["tests"])
        for result in case_results
    )

    buggy_failures = sum(
        test["buggy_status"] != "passed"
        for result in case_results
        for test in result["tests"]
    )

    fixed_passes = sum(
        test["fixed_status"] == "passed"
        for result in case_results
        for test in result["tests"]
    )

    by_category = defaultdict(list)

    for result in case_results:
        by_category[result["category"]].append(result)

    category_summary = {}

    for category, results in by_category.items():
        category_summary[category] = {
            "cases": len(results),
            "detected": sum(
                result["bug_detected"] for result in results
            ),
            "detection_rate": round(
                sum(result["bug_detected"] for result in results)
                / len(results),
                3,
            ),
        }

    return {
        "total_bug_cases": total_cases,
        "bugs_detected": detected_cases,
        "bug_detection_rate": round(
            detected_cases / total_cases, 3
        ) if total_cases else 0,
        "fixed_implementations_validated": validated_cases,
        "total_test_cases": total_tests,
        "buggy_test_failures": buggy_failures,
        "fixed_test_passes": fixed_passes,
        "category_summary": category_summary,
    }