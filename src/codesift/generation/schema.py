
import json
from dataclasses import dataclass
from typing import Any


@dataclass
class GeneratedTest:
    """One test proposed by the model."""

    name: str
    args: list[Any]
    expected: Any


@dataclass
class GeneratedTestSuite:
    """A collection of tests proposed for one function."""

    function_name: str
    tests: list[GeneratedTest]

    @classmethod
    def from_json(
        cls,
        raw: str,
        expected_function_name: str,
    ) -> "GeneratedTestSuite":
        """Parse and validate the model's JSON response."""

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Model response is not valid JSON: {exc}"
            ) from exc

        if not isinstance(data, dict):
            raise ValueError("The response must be a JSON object.")

        if set(data.keys()) != {"function_name", "tests"}:
            raise ValueError(
                "The response must contain exactly "
                "'function_name' and 'tests'."
            )

        function_name = data["function_name"]

        if function_name != expected_function_name:
            raise ValueError(
                f"Expected function '{expected_function_name}', "
                f"received '{function_name}'."
            )

        raw_tests = data["tests"]

        if not isinstance(raw_tests, list) or not raw_tests:
            raise ValueError("'tests' must be a non-empty list.")

        tests = []
        seen_names = set()

        for index, item in enumerate(raw_tests):
            if not isinstance(item, dict):
                raise ValueError(
                    f"Test {index} must be a JSON object."
                )

            if set(item.keys()) != {"name", "args", "expected"}:
                raise ValueError(
                    f"Test {index} must contain exactly "
                    "'name', 'args', and 'expected'."
                )

            name = item["name"]
            args = item["args"]

            if not isinstance(name, str) or not name.strip():
                raise ValueError(
                    f"Test {index} needs a non-empty name."
                )

            if name in seen_names:
                raise ValueError(f"Duplicate test name: {name}")

            if not isinstance(args, list):
                raise ValueError(
                    f"Arguments for test '{name}' must be a list."
                )

            # Ensure arguments and expected values are JSON-compatible.
            try:
                json.dumps(args, allow_nan=False)
                json.dumps(item["expected"], allow_nan=False)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Test '{name}' contains an unsupported value."
                ) from exc

            seen_names.add(name)
            tests.append(
                GeneratedTest(
                    name=name,
                    args=args,
                    expected=item["expected"],
                )
            )

        return cls(
            function_name=function_name,
            tests=tests,
        )
