
import inspect
import json
import time
from typing import Any
from pathlib import Path

from codesift.experiment import (
    execute_test_suite,
    evaluate_generated_suite,
)
from codesift.generation.prompts import build_test_generation_prompt
from codesift.generation.schema import GeneratedTestSuite


def get_case_source(case):
    buggy_function = case.buggy_function
    original_name = buggy_function.__name__

    if not original_name.endswith("_buggy"):
        raise ValueError(
            f"Unexpected buggy function name: {original_name}"
        )

    function_name = original_name.removesuffix("_buggy")
    source_code = inspect.getsource(buggy_function)

    source_code = source_code.replace(
        f"def {original_name}(",
        f"def {function_name}(",
        1,
    )

    if f"def {function_name}(" not in source_code:
        raise ValueError(
            f"Could not prepare source for {function_name}"
        )

    return function_name, source_code


def clean_response(raw: str) -> str:
    cleaned = raw.strip()

    if cleaned.startswith("```"):
        lines = cleaned.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        cleaned = "\n".join(lines).strip()

    return cleaned


def parse_generated_suite(
    raw_response: str,
    function_name: str,
    max_tests: int,
) -> GeneratedTestSuite:
    suite = GeneratedTestSuite.from_json(
        clean_response(raw_response),
        expected_function_name=function_name,
    )

    if len(suite.tests) > max_tests:
        raise ValueError(
            f"Model generated {len(suite.tests)} tests; "
            f"maximum allowed is {max_tests}."
        )

    return suite


def suite_to_dict(suite: GeneratedTestSuite) -> dict[str, Any]:
    return {
        "function_name": suite.function_name,
        "tests": [
            {
                "name": test.name,
                "args": test.args,
                "expected": test.expected,
            }
            for test in suite.tests
        ],
    }


def build_feedback_prompt(
    source_code: str,
    function_name: str,
    behavior_spec: str,
    initial_suite: GeneratedTestSuite,
    execution_results: list[dict[str, Any]],
    max_tests: int,
) -> str:
    feedback_data = [
        {
            "name": result["name"],
            "args": result["args"],
            "expected": result["expected"],
            "actual": result["actual"],
            "status": result["status"],
            "error": result["error"],
        }
        for result in execution_results
    ]

    return f"""
You are improving a software test suite using execution feedback.

FUNCTION NAME:
{function_name}

INTENDED BEHAVIOR:
{behavior_spec}

SOURCE CODE:
```python
{source_code}
```

ORIGINAL GENERATED TESTS:
{json.dumps(suite_to_dict(initial_suite)["tests"], indent=2)}

OBSERVED EXECUTION FEEDBACK:
{json.dumps(feedback_data, indent=2)}

TASK:
Generate an improved test suite for this function.

REQUIREMENTS:
1. Generate at most {max_tests} tests.
2. Retain useful original tests.
3. Add or revise tests where execution feedback suggests gaps.
4. Derive expected values from the intended behavior.
5. Do not change expected values just to make failing tests pass.
6. Include relevant boundary and edge cases.
7. Use unique descriptive test names.
8. Do not modify or repair the function.
9. Do not claim a test passes unless it has been executed.
10. Do not request or invent access to hidden reference tests.
11. Return valid JSON only, without Markdown fences or commentary.
12. Each test's args must be a JSON array.

REQUIRED JSON FORMAT:
{{
    "function_name": "{function_name}",
    "tests": [
        {{
            "name": "descriptive_test_name",
            "args": ["example_argument"],
            "expected": "expected_result"
        }}
    ]
}}

Return only the JSON object.
""".strip()


def generate_suite(
    provider,
    prompt: str,
    function_name: str,
    max_tests: int,
) -> tuple[GeneratedTestSuite, float]:
    start_time = time.perf_counter()

    raw_response = provider.generate(prompt)

    latency = time.perf_counter() - start_time

    try:
        suite = parse_generated_suite(
            raw_response,
            function_name,
            max_tests,
        )
    except ValueError:
        diagnostic_dir = (
            Path(__file__).resolve().parents[2]
            / "reports"
            / "diagnostics"
        )

        diagnostic_dir.mkdir(parents=True, exist_ok=True)

        diagnostic_file = (
            diagnostic_dir
            / f"invalid_response_{function_name}_{time.time_ns()}.txt"
        )

        diagnostic_file.write_text(
            raw_response or "<EMPTY MODEL RESPONSE>",
            encoding="utf-8",
        )

        print(f"Invalid model response saved to: {diagnostic_file}")

        raise

    return suite, latency


def run_case(
    case,
    provider,
    max_tests: int = 8,
) -> dict[str, Any]:

    function_name, source_code = get_case_source(case)
    behavior_spec = case.behavior_spec

    baseline_prompt = build_test_generation_prompt(
        source_code=source_code,
        function_name=function_name,
        behavior_spec=behavior_spec,
        max_tests=max_tests,
    )

    print(f"\n[{case.bug_id}] Generating shared initial test suite...")

    initial_suite, initial_latency = generate_suite(
        provider,
        baseline_prompt,
        function_name,
        max_tests,
    )

    initial_suite_dict = suite_to_dict(initial_suite)

    print(f"[{case.bug_id}] Evaluating baseline...")

    baseline_evaluation = evaluate_generated_suite(
        initial_suite,
        case,
    )

    print(f"[{case.bug_id}] Executing initial tests for feedback...")

    initial_execution = execute_test_suite(
        initial_suite,
        case.buggy_function,
    )

    feedback_prompt = build_feedback_prompt(
        source_code=source_code,
        function_name=function_name,
        behavior_spec=behavior_spec,
        initial_suite=initial_suite,
        execution_results=initial_execution,
        max_tests=max_tests,
    )

    print(f"[{case.bug_id}] Generating revised tests...")

    revised_suite, revision_latency = generate_suite(
        provider,
        feedback_prompt,
        function_name,
        max_tests,
    )

    print(f"[{case.bug_id}] Evaluating revised test suite...")

    revised_evaluation = evaluate_generated_suite(
        revised_suite,
        case,
    )

    return {
        "bug_id": case.bug_id,
        "category": case.category,
        "description": case.description,
        "function_name": function_name,
        "experiment_design": "paired_shared_initial_suite_v1",
        "generation_prompt_version": "test_generation_v2",
        "feedback_prompt_version": "execution_feedback_v1",
        "evaluator_version": "type_aware_float_tolerance_v1",
        "benchmark_version": "benchmark_v3_1",
        "baseline": {
            "suite": initial_suite_dict,
            "evaluation": baseline_evaluation,
            "generation_latency_seconds": round(
                initial_latency, 4
            ),
        },
        "feedback": {
            "initial_suite": initial_suite_dict,
            "initial_execution": initial_execution,
            "initial_evaluation": baseline_evaluation,
            "revised_suite": suite_to_dict(revised_suite),
            "revised_evaluation": revised_evaluation,
            "initial_generation_latency_seconds": round(
                initial_latency, 4
            ),
            "revision_latency_seconds": round(
                revision_latency, 4
            ),
            "total_generation_latency_seconds": round(
                initial_latency + revision_latency, 4
            ),
        },
    }
