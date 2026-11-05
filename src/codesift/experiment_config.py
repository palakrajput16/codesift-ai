
EXPERIMENT_CONFIG = {
    "CS001": {
        "function_name": "discount",
        "source_code": """
def discount(price, discount_percent):
    return price * (discount_percent / 100)
""".strip(),
    },
    "CS002": {
        "function_name": "is_adult",
        "source_code": """
def is_adult(age):
    return age > 18
""".strip(),
    },
    "CS003": {
        "function_name": "safe_average",
        "source_code": """
def safe_average(values):
    return sum(values) / len(values)
""".strip(),
    },
    "CS004": {
        "function_name": "stable_unique",
        "source_code": """
def stable_unique(values):
    return list(set(values))
""".strip(),
    },
    "CS005": {
        "function_name": "middle_values",
        "source_code": """
def middle_values(values):
    if not values:
        return []
    return [values[len(values) // 2]]
""".strip(),
    },
    "CS006": {
        "function_name": "second_largest",
        "source_code": """
def second_largest(values):
    if len(values) < 2:
        return None
    return sorted(values)[-2]
""".strip(),
    },
}
