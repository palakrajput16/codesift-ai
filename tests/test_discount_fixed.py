from codesift.fixtures import discount_fixed


def test_ten_percent_discount():
    assert discount_fixed(100, 10) == 90