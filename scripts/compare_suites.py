
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_FILE = ROOT / "reports" / "feedback_loop_results.json"
OUTPUT_FILE = ROOT / "reports" / "suite_comparison.json"


def test_key(test):
    """Compare tests by their name, arguments, and expected result."""
    return (
        test["name"],
        json.dumps(test["args"], sort_keys=True),
        json.dumps(test["expected"], sort_keys=True),
    )


def main():
    if not REPORT_FILE.exists():
        raise FileNotFoundError(
            f"Report not found: {REPORT_FILE}\n"
            "Run scripts/feedback_loop.py first."
        )

    with REPORT_FILE.open("r", encoding="utf-8") as file:
        report = json.load(file)

    # The feedback-loop report stores original results and revised tests.
    initial_results = report["initial"]["results"]
    revised_tests = report["revised"]["tests"]

    # Reconstruct the original test definitions from the execution records.
    initial_tests = [
        {
            "name": result["name"],
            "args": result["args"],
            "expected": result["expected"],
        }
        for result in initial_results
    ]

    initial_by_key = {test_key(test): test for test in initial_tests}
    revised_by_key = {test_key(test): test for test in revised_tests}

    initial_keys = set(initial_by_key)
    revised_keys = set(revised_by_key)

    unchanged = initial_keys & revised_keys
    removed = initial_keys - revised_keys
    added = revised_keys - initial_keys

    # Detect tests whose name and arguments are unchanged but whose
    # expected result was modified.
    def identity_without_expected(test):
        return (
            test["name"],
            json.dumps(test["args"], sort_keys=True),
        )

    initial_by_identity = {
        identity_without_expected(test): test for test in initial_tests
    }
    revised_by_identity = {
        identity_without_expected(test): test for test in revised_tests
    }

    changed_expected = []

    for identity in initial_by_identity.keys() & revised_by_identity.keys():
        before = initial_by_identity[identity]
        after = revised_by_identity[identity]

        if before["expected"] != after["expected"]:
            changed_expected.append({
                "name": before["name"],
                "args": before["args"],
                "initial_expected": before["expected"],
                "revised_expected": after["expected"],
            })

    comparison = {
        "initial_test_count": len(initial_tests),
        "revised_test_count": len(revised_tests),
        "unchanged_test_count": len(unchanged),
        "added_tests": [revised_by_key[k] for k in sorted(added)],
        "removed_tests": [initial_by_key[k] for k in sorted(removed)],
        "changed_expected_values": changed_expected,
        "identical_suite": initial_keys == revised_keys,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(comparison, file, indent=2)

    print("--- Test Suite Comparison ---")
    print(f"Initial tests:          {comparison['initial_test_count']}")
    print(f"Revised tests:          {comparison['revised_test_count']}")
    print(f"Unchanged tests:        {comparison['unchanged_test_count']}")
    print(f"Added tests:            {len(comparison['added_tests'])}")
    print(f"Removed tests:          {len(comparison['removed_tests'])}")
    print(f"Changed expected value:  {len(changed_expected)}")
    print(f"Identical suite:        {comparison['identical_suite']}")
    print(f"\nSaved report to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
