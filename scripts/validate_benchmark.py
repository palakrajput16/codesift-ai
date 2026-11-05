
from codesift.benchmark import BENCHMARK
from codesift.experiment import values_match


def run_test(function, test):
    try:
        actual = function(*test.args)

        return {
            "status": "PASS" if values_match(actual, test.expected) else "FAIL",
            "actual": actual,
        }

    except Exception as exc:
        return {
            "status": "ERROR",
            "actual": f"{type(exc).__name__}: {exc}",
        }


def main():
    print("\nBENCHMARK VALIDATION")
    print("=" * 65)

    all_valid = True

    for case in BENCHMARK:
        fixed_results = [
            run_test(case.fixed_function, test)
            for test in case.tests
        ]

        buggy_results = [
            run_test(case.buggy_function, test)
            for test in case.tests
        ]

        fixed_passed = all(
            result["status"] == "PASS"
            for result in fixed_results
        )

        detected_count = sum(
            buggy["status"] in ("FAIL", "ERROR")
            and fixed["status"] == "PASS"
            for buggy, fixed in zip(buggy_results, fixed_results)
        )

        false_positive_count = sum(
            result["status"] in ("FAIL", "ERROR")
            for result in fixed_results
        )

        valid = fixed_passed and detected_count > 0
        all_valid = all_valid and valid

        print(f"\n{case.bug_id} - {case.description}")
        print(f"  Fixed tests passed: {sum(r['status'] == 'PASS' for r in fixed_results)}/{len(case.tests)}")
        print(f"  Bug-detecting tests: {detected_count}")
        print(f"  Fixed implementation failures: {false_positive_count}")
        print(f"  Validation: {'PASS' if valid else 'FAIL'}")

        if not valid:
            print("  Details:")
            for test, buggy, fixed in zip(case.tests, buggy_results, fixed_results):
                print(
                    f"    {test.name}: "
                    f"buggy={buggy['status']} "
                    f"(actual={buggy['actual']}), "
                    f"fixed={fixed['status']} "
                    f"(actual={fixed['actual']})"
                )

    print("\n" + "=" * 65)

    if all_valid:
        print("SUCCESS: All 18 benchmark cases passed validation.")
    else:
        print("WARNING: Some benchmark cases need correction.")


if __name__ == "__main__":
    main()
