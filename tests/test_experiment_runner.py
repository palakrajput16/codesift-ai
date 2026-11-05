
import json

from codesift.benchmark import BENCHMARK
from codesift.experiment_runner import run_case


class MockProvider:
    model = "mock-model"

    def __init__(self):
        self.calls = 0
        self.prompts = []

    def generate(self, prompt):
        self.calls += 1
        self.prompts.append(prompt)

        if self.calls == 2:
            tests = [
                {
                    "name": "boundary_18",
                    "args": [18],
                    "expected": True,
                },
                {
                    "name": "boundary_21",
                    "args": [21],
                    "expected": True,
                },
            ]
        else:
            tests = [
                {
                    "name": "boundary_18",
                    "args": [18],
                    "expected": True,
                }
            ]

        return json.dumps({
            "function_name": "is_adult",
            "tests": tests,
        })


def test_run_case_executes_two_generation_calls():
    case = next(
        case for case in BENCHMARK
        if case.bug_id == "CS002"
    )

    provider = MockProvider()

    result = run_case(
        case=case,
        provider=provider,
        max_tests=5,
    )

    assert provider.calls == 2
    assert result["bug_id"] == "CS002"


def test_run_case_returns_both_experimental_conditions():
    case = next(
        case for case in BENCHMARK
        if case.bug_id == "CS002"
    )

    result = run_case(
        case=case,
        provider=MockProvider(),
        max_tests=5,
    )

    assert "baseline" in result
    assert "feedback" in result
    assert "evaluation" in result["baseline"]
    assert "initial_evaluation" in result["feedback"]
    assert "revised_evaluation" in result["feedback"]


def test_feedback_condition_records_initial_and_revised_suites():
    case = next(
        case for case in BENCHMARK
        if case.bug_id == "CS002"
    )

    result = run_case(
        case=case,
        provider=MockProvider(),
        max_tests=5,
    )

    feedback = result["feedback"]

    assert len(feedback["initial_suite"]["tests"]) == 1
    assert len(feedback["revised_suite"]["tests"]) == 2
    assert feedback["revision_latency_seconds"] >= 0


def test_both_conditions_use_the_same_initial_suite():
    case = next(
        case for case in BENCHMARK
        if case.bug_id == "CS002"
    )

    result = run_case(
        case=case,
        provider=MockProvider(),
        max_tests=5,
    )

    baseline_suite = result["baseline"]["suite"]
    feedback_initial_suite = result["feedback"]["initial_suite"]

    assert baseline_suite == feedback_initial_suite


def test_feedback_prompt_contains_execution_results():
    case = next(
        case for case in BENCHMARK
        if case.bug_id == "CS002"
    )

    provider = MockProvider()

    run_case(
        case=case,
        provider=provider,
        max_tests=5,
    )

    assert len(provider.prompts) == 2
    assert "OBSERVED EXECUTION FEEDBACK" in provider.prompts[1]
    assert "boundary_18" in provider.prompts[1]
