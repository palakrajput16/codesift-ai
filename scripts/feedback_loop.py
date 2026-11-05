
import json
from pathlib import Path

from codesift.generation import GeneratedTestSuite
from codesift.models import GeminiProvider


ROOT = Path(__file__).resolve().parents[1]

SUITE_FILE = ROOT / "reports" / "generated_tests_demo.json"
RESULTS_FILE = ROOT / "reports" / "demo_execution_results.json"
OUTPUT_FILE = ROOT / "reports" / "feedback_loop_results.json"

FUNCTION_NAME = "is_adult"
BEHAVIOR_SPEC = (
    "An adult is a person whose age is greater than or equal to 18."
)

# This is a trusted local fixture, not model-generated code.
def is_adult(age):
    return age > 18


TRUSTED_TARGETS = {
    "is_adult": is_adult,
}


def read_json(path):
    if not path.exists():
        raise FileNotFoundError(
            f"Required file not found: {path}\n"
            "Run the generation and execution demos first."
        )

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def run_tests(suite_data, target):
    results = []

    for test in suite_data["tests"]:
        try:
            actual = target(*test["args"])
            expected = test["expected"]
            passed = actual == expected

            results.append({
                "name": test["name"],
                "args": test["args"],
                "expected": expected,
                "actual": actual,
                "status": "PASS" if passed else "FAIL",
                "error": None,
            })

        except Exception as exc:
            results.append({
                "name": test["name"],
                "args": test["args"],
                "expected": test["expected"],
                "actual": None,
                "status": "ERROR",
                "error": f"{type(exc).__name__}: {exc}",
            })

    return results


def summarize(results):
    return {
        "total": len(results),
        "passed": sum(r["status"] == "PASS" for r in results),
        "failed": sum(r["status"] == "FAIL" for r in results),
        "errors": sum(r["status"] == "ERROR" for r in results),
    }


def main():
    initial_suite = read_json(SUITE_FILE)
    initial_results = read_json(RESULTS_FILE)

    function_name = initial_suite["function_name"]
    target = TRUSTED_TARGETS.get(function_name)

    if target is None:
        raise ValueError(
            f"{function_name!r} is not a trusted local target."
        )

    source_code = """def is_adult(age):
    return age > 18
"""

    # Give the model execution observations, not hidden reference answers
    # or the correct implementation.
    feedback = [
        {
            "name": result["name"],
            "args": result["args"],
            "expected": result["expected"],
            "actual": result["actual"],
            "status": result["status"],
            "error": result["error"],
        }
        for result in initial_results["results"]
    ]

    prompt = f"""
You are improving a software test suite.

Function name: {function_name}

Behavior specification:
{BEHAVIOR_SPEC}

Implementation under test:
```python
{source_code}
```

Original generated tests:
{json.dumps(initial_suite["tests"], indent=2)}

Observed execution feedback:
{json.dumps(feedback, indent=2)}

Task:
Generate an improved test suite for this function.

Requirements:
- Return JSON only, with no Markdown fences or commentary.
- Use this format:
  {{
    "function_name": "{function_name}",
    "tests": [
      {{
        "name": "test_descriptive_name",
        "args": [18],
        "expected": true
      }}
    ]
  }}
- Preserve the behavior specification when determining expected values.
- Do not change expected values just to make a failing test pass.
- Retain useful original tests and add or revise tests where appropriate.
- Use unique test names.
- Include boundary cases and other useful edge cases.
- Each test's args must be a JSON array.
- Expected values must be JSON values.
- Do not return Python code.
- Do not claim that any test passes unless it has been executed.
- Return at most 10 tests.
"""

    print("Requesting test revisions using execution feedback...", flush=True)

    provider = GeminiProvider()
    raw_response = provider.generate(prompt)

    # Support a response wrapped in Markdown fences, if necessary.
    cleaned = raw_response.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    try:
        revised_data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Gemini did not return valid JSON. "
            "Inspect the model response before retrying."
        ) from exc

    # Validate the model's output against CodeSift's schema.
    validated_suite = GeneratedTestSuite.from_json(
        json.dumps(revised_data),
        expected_function_name=function_name,
    )

    # Execute only the arguments from validated JSON against the trusted
    # local function. Never execute model-generated Python source code.
    revised_results = run_tests(
        revised_data,
        target,
    )

    report = {
        "project": "CodeSift",
        "stage": "milestone_3_execution_feedback",
        "model": provider.model,
        "function_name": function_name,
        "initial": {
            "summary": summarize(initial_results["results"]),
            "results": initial_results["results"],
        },
        "revised": {
            "tests": revised_data["tests"],
            "summary": summarize(revised_results),
            "results": revised_results,
        },
        "validation": "passed",
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print("\n--- Initial Results ---")
    print(json.dumps(report["initial"]["summary"], indent=2))

    print("\n--- Revised Results ---")
    for result in revised_results:
        print(
            f"[{result['status']}] {result['name']} | "
            f"expected={result['expected']!r}, "
            f"actual={result['actual']!r}"
        )

    print(json.dumps(report["revised"]["summary"], indent=2))
    print(f"\nSaved report to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
