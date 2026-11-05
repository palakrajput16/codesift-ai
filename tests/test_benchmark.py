from codesift.benchmark import BENCHMARK
from codesift.runner import evaluate_bug_case


def test_benchmark_has_unique_ids():
    ids = [case.bug_id for case in BENCHMARK]
    assert len(ids) == len(set(ids))


def test_every_fixed_implementation_passes():
    for case in BENCHMARK:
        result = evaluate_bug_case(case)

        assert result["fixed_passed_all"], (
            f"{case.bug_id}: corrected implementation failed"
        )


def test_every_seeded_bug_is_detectable():
    for case in BENCHMARK:
        result = evaluate_bug_case(case)

        assert result["bug_detected"], (
            f"{case.bug_id}: bug was not reliably detected"
        )


def test_each_case_has_test_cases():
    for case in BENCHMARK:
        assert len(case.tests) >= 2