
import json


def build_test_generation_prompt(
    source_code: str,
    function_name: str,
    behavior_spec: str,
    max_tests: int = 8,
) -> str:
    """
    Build a prompt using only the target code and its
    intended behavior. Do not pass hidden benchmark data here.
    """

    if not source_code.strip():
        raise ValueError("Source code cannot be empty.")

    if not function_name.strip():
        raise ValueError("Function name cannot be empty.")

    if not behavior_spec.strip():
        raise ValueError("Behavior specification cannot be empty.")

    if not 1 <= max_tests <= 20:
        raise ValueError("max_tests must be between 1 and 20.")

    output_format = {
        "function_name": function_name,
        "tests": [
            {
                "name": "descriptive_test_name",
                "args": ["example_argument"],
                "expected": "expected_result",
            }
        ],
    }

    return f"""
You are a software testing assistant.

Your task is to propose tests for the supplied function.

FUNCTION NAME:
{function_name}

INTENDED BEHAVIOR:
{behavior_spec}

SOURCE CODE:
```python
{source_code}
```

INSTRUCTIONS:
1. Generate at most {max_tests} useful test cases.
2. Cover ordinary inputs, boundary conditions, and relevant edge cases.
3. Derive expected results from the intended behavior, not merely
   from the current implementation.
4. Do not assume the implementation is correct.
5. Do not modify or repair the function.
6. Do not request or invent access to hidden reference tests.
7. Return only valid JSON, with no Markdown fences or commentary.
8. Each test's args field must be a JSON array of positional arguments.
9. Use JSON values for expected results.
10. Give each test a unique, descriptive name.
11. Return strictly valid JSON, not Python dictionary syntax.
12. Use lowercase JSON literals: true, false, and null.
13. Never use Python literals such as True, False, or None.
14. Use double quotes for all JSON strings and property names.
15. Do not include comments or trailing commas in the JSON.
16. Keep test arguments consistent with the function's input types.
17. Do not introduce unrelated mixed-type inputs unless the
    intended behavior explicitly requires them.
18. Ensure the complete response can be parsed by Python's json.loads().

IMPORTANT JSON RULES:
- Boolean values must be true or false, never True or False.
- Null values must be null, never None.
- Use double quotes for all JSON strings and property names.
- Do not include comments or trailing commas.
- Return exactly one JSON object.

REQUIRED JSON SHAPE:
{json.dumps(output_format, indent=2)}

Return only the JSON object.
""".strip()
