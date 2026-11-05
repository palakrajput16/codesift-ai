
from dataclasses import dataclass
from typing import Any, Callable

from codesift import fixtures


@dataclass
class TestCase:
    name: str
    args: tuple[Any, ...]
    expected: Any


@dataclass
class BugCase:
    bug_id: str
    category: str
    description: str
    behavior_spec: str
    buggy_function: Callable
    fixed_function: Callable
    tests: list[TestCase]


BENCHMARK = [
    BugCase(
        bug_id="CS001",
        category="arithmetic",
        description="Incorrect final price after a discount",
        behavior_spec=(
            "Calculate the final price after applying a percentage discount. "
            "The discount must be subtracted from the original price. "
            "A zero percent discount must leave the original price unchanged."
        ),
        buggy_function=fixtures.discount_buggy,
        fixed_function=fixtures.discount_fixed,
        tests=[
            TestCase("ten_percent", (100, 10), 90),
            TestCase("twenty_five_percent", (200, 25), 150),
            TestCase("zero_discount", (100, 0), 100),
        ],
    ),
    BugCase(
        bug_id="CS002",
        category="boundary",
        description="Incorrect adult-age boundary",
        behavior_spec=(
            "Return True when the person's age is 18 or older. "
            "Return False when the person's age is below 18."
        ),
        buggy_function=fixtures.is_adult_buggy,
        fixed_function=fixtures.is_adult_fixed,
        tests=[
            TestCase("below_boundary", (17,), False),
            TestCase("at_boundary", (18,), True),
            TestCase("above_boundary", (21,), True),
        ],
    ),
    BugCase(
        bug_id="CS003",
        category="edge_case",
        description="Average calculation fails on empty input",
        behavior_spec=(
            "Calculate the arithmetic mean of a list of numbers. "
            "Return None when the list is empty. "
            "Return the number itself when the list contains one value."
        ),
        buggy_function=fixtures.safe_average_buggy,
        fixed_function=fixtures.safe_average_fixed,
        tests=[
            TestCase("ordinary_average", ([2, 4],), 3),
            TestCase("empty_input", ([],), None),
            TestCase("single_value", ([5],), 5),
        ],
    ),
    BugCase(
        bug_id="CS004",
        category="data_processing",
        description="Duplicate removal must preserve order",
        behavior_spec=(
            "The function accepts a list of integers. "
            "Remove duplicate integer values while preserving "
            "the order of their first occurrences. "
            "An empty list must return an empty list."
        ),
        buggy_function=fixtures.stable_unique_buggy,
        fixed_function=fixtures.stable_unique_fixed,
        tests=[
            TestCase("repeated_values", ([3, 1, 3, 2],), [3, 1, 2]),
            TestCase("empty_list", ([],), []),
            TestCase("already_unique", ([1, 2, 3],), [1, 2, 3]),
        ],
    ),
    BugCase(
        bug_id="CS005",
        category="logic",
        description="Middle-value calculation fails on even-length input",
        behavior_spec=(
            "The function accepts a list of integers sorted in ascending order. "
            "Return the middle value when the list length is odd. "
            "When its length is even, return the two middle values "
            "in their existing ascending order. "
            "Return an empty list for empty input. "
            "Do not sort or modify the input."
        ),
        buggy_function=fixtures.middle_values_buggy,
        fixed_function=fixtures.middle_values_fixed,
        tests=[
            TestCase("odd_length", ([1, 2, 3],), [2]),
            TestCase("even_length", ([1, 2, 3, 4],), [2, 3]),
            TestCase("empty_list", ([],), []),
        ],
    ),
    BugCase(
        bug_id="CS006",
        category="data_processing",
        description="Second-largest calculation does not handle duplicate values",
        behavior_spec=(
            "Return the second-largest distinct value in a list of integers. "
            "Duplicate values must count only once. "
            "Return None if fewer than two distinct values exist."
        ),
        buggy_function=fixtures.second_largest_buggy,
        fixed_function=fixtures.second_largest_fixed,
        tests=[
            TestCase("distinct_values", ([5, 4, 3, 2],), 4),
            TestCase("duplicate_largest", ([5, 5, 3, 2],), 3),
            TestCase("all_duplicates", ([1, 1, 1],), None),
            TestCase("two_distinct_values", ([8, 8, 5],), 5),
        ],
    ),
    BugCase(
        bug_id="CS007",
        category="boundary",
        description="Tax threshold comparison is incorrect",
        behavior_spec=(
            "Calculate tax at the given rate when income is greater than "
            "or equal to the threshold. Return zero when income is below "
            "the threshold."
        ),
        buggy_function=fixtures.calculate_tax_buggy,
        fixed_function=fixtures.calculate_tax_fixed,
        tests=[
            TestCase("below_threshold", (900, 10, 1000), 0),
            TestCase("at_threshold", (1000, 10, 1000), 100),
            TestCase("above_threshold", (1200, 10, 1000), 120),
        ],
    ),
    BugCase(
        bug_id="CS008",
        category="boundary",
        description="Free shipping threshold is incorrect",
        behavior_spec=(
            "Shipping costs 50 when the order total is below 500. "
            "Shipping is free when the order total is 500 or more."
        ),
        buggy_function=fixtures.calculate_shipping_buggy,
        fixed_function=fixtures.calculate_shipping_fixed,
        tests=[
            TestCase("below_threshold", (499,), 50),
            TestCase("at_threshold", (500,), 0),
            TestCase("above_threshold", (501,), 0),
        ],
    ),
    BugCase(
        bug_id="CS009",
        category="logic",
        description="Leap year calculation ignores century rules",
        behavior_spec=(
            "A leap year is divisible by 400, or divisible by 4 "
            "but not divisible by 100."
        ),
        buggy_function=fixtures.is_leap_year_buggy,
        fixed_function=fixtures.is_leap_year_fixed,
        tests=[
            TestCase("ordinary_leap_year", (2024,), True),
            TestCase("ordinary_non_leap_year", (2023,), False),
            TestCase("century_non_leap_year", (1900,), False),
            TestCase("four_hundred_year", (2000,), True),
        ],
    ),
    BugCase(
        bug_id="CS010",
        category="boundary",
        description="Clamping changes values equal to the upper bound",
        behavior_spec=(
            "Clamp a value between lower and upper bounds, inclusive. "
            "Values below the lower bound return the lower bound. "
            "Values above the upper bound return the upper bound."
        ),
        buggy_function=fixtures.clamp_value_buggy,
        fixed_function=fixtures.clamp_value_fixed,
        tests=[
            TestCase("below_lower", (2, 5, 10), 5),
            TestCase("inside_range", (7, 5, 10), 7),
            TestCase("at_upper", (10, 5, 10), 10),
            TestCase("above_upper", (12, 5, 10), 10),
        ],
    ),
    BugCase(
        bug_id="CS011",
        category="edge_case",
        description="Occurrence counter skips the final element",
        behavior_spec=(
            "Count every occurrence of the target value in the input list, "
            "including the final element."
        ),
        buggy_function=fixtures.count_occurrences_buggy,
        fixed_function=fixtures.count_occurrences_fixed,
        tests=[
            TestCase("target_at_start", ([2, 1, 3], 2), 1),
            TestCase("target_at_end", ([1, 3, 2], 2), 1),
            TestCase("multiple_occurrences", ([2, 1, 2, 2], 2), 3),
            TestCase("empty_list", ([], 2), 0),
        ],
    ),
    BugCase(
        bug_id="CS012",
        category="algorithm",
        description="Merging sorted lists loses equal elements",
        behavior_spec=(
            "Merge two ascending sorted integer lists into one ascending "
            "list, preserving every element, including duplicates."
        ),
        buggy_function=fixtures.merge_sorted_buggy,
        fixed_function=fixtures.merge_sorted_fixed,
        tests=[
            TestCase("no_equal_values", ([1, 3], [2, 4]), [1, 2, 3, 4]),
            TestCase("equal_values", ([1, 2], [2, 3]), [1, 2, 2, 3]),
            TestCase("empty_left", ([], [1, 2]), [1, 2]),
            TestCase("empty_right", ([1, 2], []), [1, 2]),
        ],
    ),
    BugCase(
        bug_id="CS013",
        category="algorithm",
        description="Binary search misses the final candidate position",
        behavior_spec=(
            "Return the zero-based index of the target in a sorted list. "
            "Return -1 if the target is not present."
        ),
        buggy_function=fixtures.binary_search_buggy,
        fixed_function=fixtures.binary_search_fixed,
        tests=[
            TestCase("first_element", ([1, 3, 5, 7], 1), 0),
            TestCase("middle_element", ([1, 3, 5, 7], 5), 2),
            TestCase("last_element", ([1, 3, 5, 7], 7), 3),
            TestCase("missing_element", ([1, 3, 5, 7], 4), -1),
        ],
    ),
    BugCase(
        bug_id="CS014",
        category="logic",
        description="Removing negative numbers also removes zero",
        behavior_spec=(
            "Remove negative integers from the list. Preserve zero and "
            "all positive integers in their original order."
        ),
        buggy_function=fixtures.remove_negatives_buggy,
        fixed_function=fixtures.remove_negatives_fixed,
        tests=[
            TestCase("mixed_values", ([-2, 0, 3, -1, 4],), [0, 3, 4]),
            TestCase("only_negatives", ((-1, -2),), []),
            TestCase("only_nonnegative", ([0, 1, 2],), [0, 1, 2]),
        ],
    ),
    BugCase(
        bug_id="CS015",
        category="data_processing",
        description="Word frequency counting is case-sensitive",
        behavior_spec=(
            "Count word frequencies without distinguishing uppercase "
            "and lowercase versions of the same word. Words are separated "
            "by whitespace."
        ),
        buggy_function=fixtures.word_frequency_buggy,
        fixed_function=fixtures.word_frequency_fixed,
        tests=[
            TestCase("repeated_word", ("cat cat dog",), {"cat": 2, "dog": 1}),
            TestCase("mixed_case", ("Cat cat CAT",), {"cat": 3}),
            TestCase("empty_sentence", ("",), {}),
        ],
    ),
    BugCase(
        bug_id="CS016",
        category="edge_case",
        description="List rotation does not normalize large shifts",
        behavior_spec=(
            "Rotate a list to the right by k positions. "
            "Rotation amounts greater than the list length must be "
            "normalized. An empty list returns an empty list."
        ),
        buggy_function=fixtures.rotate_list_buggy,
        fixed_function=fixtures.rotate_list_fixed,
        tests=[
            TestCase("one_position", ([1, 2, 3, 4], 1), [4, 1, 2, 3]),
            TestCase("full_rotation", ([1, 2, 3], 3), [1, 2, 3]),
            TestCase("large_rotation", ([1, 2, 3], 5), [2, 3, 1]),
            TestCase("empty_list", ([], 4), []),
        ],
    ),
    BugCase(
        bug_id="CS017",
        category="string_processing",
        description="Palindrome check does not ignore spaces",
        behavior_spec=(
            "Check whether a string is a palindrome, ignoring differences "
            "in letter case and ignoring whitespace."
        ),
        buggy_function=fixtures.is_palindrome_buggy,
        fixed_function=fixtures.is_palindrome_fixed,
        tests=[
            TestCase("simple_palindrome", ("level",), True),
            TestCase("mixed_case", ("RaceCar",), True),
            TestCase("spaces", ("nurses run",), True),
            TestCase("not_palindrome", ("hello",), False),
        ],
    ),
    BugCase(
        bug_id="CS018",
        category="boundary",
        description="Missing-number calculation excludes the upper endpoint",
        behavior_spec=(
            "The input contains distinct integers from 1 to upper_bound "
            "with exactly one number missing. Return the missing number."
        ),
        buggy_function=fixtures.find_missing_number_buggy,
        fixed_function=fixtures.find_missing_number_fixed,
        tests=[
            TestCase("missing_middle", ([1, 2, 4, 5], 5), 3),
            TestCase("missing_upper", ([1, 2, 3, 4], 5), 5),
            TestCase("missing_lower", ([2, 3, 4, 5], 5), 1),
        ],
    ),
]
