
import json
from pathlib import Path

from codesift.generation.prompts import build_test_generation_prompt
from codesift.generation.schema import GeneratedTestSuite
from codesift.models.gemini_provider import GeminiProvider


def main():
    source_code = """
def is_adult(age: int) -> bool:
    return age > 18
""".strip()

    function_name = "is_adult"
    behavior_spec = (
        "Return True when age is 18 or older. "
        "Return False when age is below 18."
    )

    prompt = build_test_generation_prompt(
        source_code=source_code,
        function_name=function_name,
        behavior_spec=behavior_spec,
        max_tests=5,
    )

    provider = GeminiProvider()
    print(f"Generating tests with model: {provider.model}")

    raw_response = provider.generate(prompt)

    suite = GeneratedTestSuite.from_json(
        raw_response,
        expected_function_name=function_name,
    )

    report = {
        "project": "CodeSift",
        "stage": "milestone_3_ai_generation_demo",
        "model": provider.model,
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

    output_path = (
        Path(__file__).resolve().parents[1]
        / "reports"
        / "generated_tests_demo.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\nGenerated {len(suite.tests)} tests:")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nSaved report to: {output_path}")


if __name__ == "__main__":
    main()
