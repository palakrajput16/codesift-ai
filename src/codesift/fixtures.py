
def discount_buggy(price: float, discount_percent: float) -> float:
    """Bug: returns the discount amount instead of the final price."""
    return price * (discount_percent / 100)


def discount_fixed(price: float, discount_percent: float) -> float:
    """Correctly calculates the final price after a discount."""
    return price * (1 - discount_percent / 100)


def is_adult_buggy(age: int) -> bool:
    """Bug: incorrectly treats an 18-year-old as not an adult."""
    return age > 18


def is_adult_fixed(age: int) -> bool:
    return age >= 18


def safe_average_buggy(values: list[float]) -> float:
    """Bug: crashes when the list is empty."""
    return sum(values) / len(values)


def safe_average_fixed(values: list[float]) -> float | None:
    """Returns None when no average can be calculated."""
    if not values:
        return None
    return sum(values) / len(values)


def stable_unique_buggy(values: list[int]) -> list[int]:
    """Bug: set conversion does not guarantee preserving input order."""
    return list(set(values))


def stable_unique_fixed(values: list[int]) -> list[int]:
    """Removes duplicates while preserving first-occurrence order."""
    result = []
    seen = set()

    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)

    return result


def middle_values_buggy(values: list[int]) -> list[int]:
    """Bug: returns only one middle element, even for even-length lists."""
    if not values:
        return []
    return [values[len(values) // 2]]


def middle_values_fixed(values: list[int]) -> list[int]:
    """Returns the central element, or both central elements."""
    if not values:
        return []

    middle = len(values) // 2

    if len(values) % 2 == 1:
        return [values[middle]]

    return values[middle - 1:middle + 1]


def second_largest_buggy(values: list[int]) -> int | None:
    """Bug: does not account for duplicate values."""
    if len(values) < 2:
        return None
    return sorted(values)[-2]


def second_largest_fixed(values: list[int]) -> int | None:
    """Returns the second-largest distinct value."""
    unique_values = sorted(set(values))

    if len(unique_values) < 2:
        return None

    return unique_values[-2]


# CS007: Tax threshold

def calculate_tax_buggy(income: float, rate: float, threshold: float) -> float:
    """Bug: excludes income exactly equal to the threshold."""
    if income > threshold:
        return income * rate / 100
    return 0.0


def calculate_tax_fixed(income: float, rate: float, threshold: float) -> float:
    if income >= threshold:
        return income * rate / 100
    return 0.0


# CS008: Free shipping threshold

def calculate_shipping_buggy(order_total: float) -> float:
    """Bug: uses an incorrect free-shipping threshold."""
    return 0.0 if order_total > 500 else 50.0


def calculate_shipping_fixed(order_total: float) -> float:
    return 0.0 if order_total >= 500 else 50.0


# CS009: Leap year

def is_leap_year_buggy(year: int) -> bool:
    """Bug: treats every year divisible by four as a leap year."""
    return year % 4 == 0


def is_leap_year_fixed(year: int) -> bool:
    return year % 400 == 0 or (year % 4 == 0 and year % 100 != 0)


# CS010: Clamp value

def clamp_value_buggy(value: float, lower: float, upper: float) -> float:
    """Bug: incorrectly handles values equal to the upper bound."""
    if value >= upper:
        return upper - 1
    if value < lower:
        return lower
    return value


def clamp_value_fixed(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))


# CS011: Count occurrences

def count_occurrences_buggy(values: list[int], target: int) -> int:
    """Bug: skips the final element."""
    return sum(1 for value in values[:-1] if value == target)


def count_occurrences_fixed(values: list[int], target: int) -> int:
    return sum(1 for value in values if value == target)


# CS012: Merge sorted lists

def merge_sorted_buggy(left, right):
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        elif left[i] > right[j]:
            result.append(right[j])
            j += 1
        else:
            # Bug: one copy of an equal value is lost
            result.append(left[i])
            i += 1
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result

def merge_sorted_fixed(left: list[int], right: list[int]) -> list[int]:
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result


# CS013: Binary search

def binary_search_buggy(values: list[int], target: int) -> int:
    """Bug: excludes the final candidate position."""
    low, high = 0, len(values) - 1

    while low < high:
        mid = (low + high) // 2

        if values[mid] == target:
            return mid
        if values[mid] < target:
            low = mid + 1
        else:
            high = mid - 1

    return -1


def binary_search_fixed(values: list[int], target: int) -> int:
    low, high = 0, len(values) - 1

    while low <= high:
        mid = (low + high) // 2

        if values[mid] == target:
            return mid
        if values[mid] < target:
            low = mid + 1
        else:
            high = mid - 1

    return -1


# CS014: Remove negative numbers

def remove_negatives_buggy(values: list[int]) -> list[int]:
    """Bug: also removes zero."""
    return [value for value in values if value > 0]


def remove_negatives_fixed(values: list[int]) -> list[int]:
    return [value for value in values if value >= 0]


# CS015: Word frequency

def word_frequency_buggy(sentence: str) -> dict[str, int]:
    """Bug: treats uppercase and lowercase words as different."""
    counts = {}

    for word in sentence.split():
        counts[word] = counts.get(word, 0) + 1

    return counts


def word_frequency_fixed(sentence: str) -> dict[str, int]:
    counts = {}

    for word in sentence.lower().split():
        counts[word] = counts.get(word, 0) + 1

    return counts


# CS016: Rotate list

def rotate_list_buggy(values: list[int], k: int) -> list[int]:
    """Bug: fails to normalize rotation amounts."""
    if not values:
        return []
    return values[-k:] + values[:-k]


def rotate_list_fixed(values: list[int], k: int) -> list[int]:
    if not values:
        return []

    k %= len(values)
    return values[-k:] + values[:-k] if k else values[:]


# CS017: Palindrome

def is_palindrome_buggy(value: str) -> bool:
    """Bug: spaces are not ignored."""
    return value.lower() == value.lower()[::-1]


def is_palindrome_fixed(value: str) -> bool:
    normalized = "".join(char.lower() for char in value if not char.isspace())
    return normalized == normalized[::-1]


# CS018: Missing number

def find_missing_number_buggy(values: list[int], upper_bound: int) -> int:
    """Bug: excludes the upper bound from the expected range."""
    expected = set(range(1, upper_bound))
    return next(iter(expected - set(values)), -1)


def find_missing_number_fixed(values: list[int], upper_bound: int) -> int:
    """Finds the one missing number in the range 1 to upper_bound."""
    expected = set(range(1, upper_bound + 1))
    missing = expected - set(values)

    if len(missing) != 1:
        raise ValueError("Expected exactly one missing number")

    return next(iter(missing))
