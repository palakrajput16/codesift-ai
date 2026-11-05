
from codesift.benchmark import BENCHMARK
from codesift.experiment import (
    execute_test_suite,
    evaluate_generated_suite,
    evaluate_hidden_tests,
    values_match,
)
from codesift.generation.schema import GeneratedTest, GeneratedTestSuite


def make_suite(tests):
    return GeneratedTestSuite(
        function_name="is_adult",
        tests=[
            GeneratedTest(
                name=name,
                args=args,
                expected=expected,
            )
            for name, args, expected in tests
        ],
    )


def test_generated_suite_detects_bug():
    case = next(c for c in BENCHMARK if c.bug_id == "CS002")

    suite = make_suite([
        ("adult_boundary", [18], True),
        ("above_boundary", [21], True),
    ])

    result = evaluate_generated_suite(suite, case)

    assert result["bug_detected"] is True
    assert result["detected_test_count"] == 1
    assert result["false_positive_count"] == 0


def test_incorrect_expected_value_is_false_positive():
    case = next(c for c in BENCHMARK if c.bug_id == "CS002")

    suite = make_suite([
        ("incorrect_boundary", [18], False),
    ])

    result = evaluate_generated_suite(suite, case)

    assert result["bug_detected"] is False
    assert result["false_positive_count"] == 1


def test_execute_test_suite_records_errors():
    def failing_function(value):
        raise ValueError("Invalid input")

    suite = make_suite([
        ("error_case", [10], 10),
    ])

    results = execute_test_suite(suite, failing_function)

    assert len(results) == 1
    assert results[0]["status"] == "ERROR"
    assert "ValueError" in results[0]["error"]


def test_hidden_test_evaluation():
    case = next(c for c in BENCHMARK if c.bug_id == "CS002")

    results = evaluate_hidden_tests(
        case.fixed_function,
        case.tests,
    )

    assert len(results) == 3
    assert all(result["status"] == "PASS" for result in results)


def test_float_comparison_uses_tolerance():
    assert values_match(84.49154999999999, 84.49155)


def test_boolean_does_not_match_integer():
    assert not values_match(True, 1)
    assert not values_match(False, 0)


def test_lists_compare_float_values_with_tolerance():
    assert values_match(
        [84.49154999999999, 10.0],
        [84.49155, 10.0],
    )


def test_lists_reject_boolean_integer_mismatch():
    assert not values_match(
        [True, False],
        [1, 0],
    )


def test_nested_collections_compare_correctly():
    actual = {"result": [84.49154999999999, True]}
    expected = {"result": [84.49155, True]}

    assert values_match(actual, expected)
