
import pytest

from codesift.generation.prompts import (
    build_test_generation_prompt,
)
from codesift.generation.schema import GeneratedTestSuite


def test_valid_json_is_parsed():
    raw = """
    {
        "function_name": "is_adult",
        "tests": [
            {
                "name": "age_at_boundary",
                "args": [18],
                "expected": true
            },
            {
                "name": "below_boundary",
                "args": [17],
                "expected": false
            }
        ]
    }
    """

    suite = GeneratedTestSuite.from_json(
        raw,
        expected_function_name="is_adult",
    )

    assert suite.function_name == "is_adult"
    assert len(suite.tests) == 2
    assert suite.tests[0].args == [18]
    assert suite.tests[0].expected is True


def test_invalid_json_is_rejected():
    with pytest.raises(ValueError, match="valid JSON"):
        GeneratedTestSuite.from_json(
            "this is not JSON",
            expected_function_name="is_adult",
        )


def test_wrong_function_name_is_rejected():
    raw = """
    {
        "function_name": "other_function",
        "tests": [
            {
                "name": "example",
                "args": [18],
                "expected": true
            }
        ]
    }
    """

    with pytest.raises(ValueError, match="Expected function"):
        GeneratedTestSuite.from_json(
            raw,
            expected_function_name="is_adult",
        )


def test_duplicate_test_names_are_rejected():
    raw = """
    {
        "function_name": "is_adult",
        "tests": [
            {
                "name": "same_name",
                "args": [18],
                "expected": true
            },
            {
                "name": "same_name",
                "args": [17],
                "expected": false
            }
        ]
    }
    """

    with pytest.raises(ValueError, match="Duplicate test name"):
        GeneratedTestSuite.from_json(
            raw,
            expected_function_name="is_adult",
        )


def test_empty_test_suite_is_rejected():
    raw = '{"function_name": "is_adult", "tests": []}'

    with pytest.raises(ValueError, match="non-empty list"):
        GeneratedTestSuite.from_json(
            raw,
            expected_function_name="is_adult",
        )


def test_prompt_contains_spec_and_source():
    prompt = build_test_generation_prompt(
        source_code="def is_adult(age): return age > 18",
        function_name="is_adult",
        behavior_spec="A person is an adult at age 18 or older.",
    )

    assert "A person is an adult at age 18 or older." in prompt
    assert "def is_adult(age): return age > 18" in prompt
    assert "Return only valid JSON" in prompt


def test_prompt_rejects_empty_source():
    with pytest.raises(ValueError, match="Source code"):
        build_test_generation_prompt(
            source_code="",
            function_name="is_adult",
            behavior_spec="A person is an adult at age 18 or older.",
        )
