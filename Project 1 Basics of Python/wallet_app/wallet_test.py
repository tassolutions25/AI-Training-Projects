import unittest
import re


def is_valid_phone(phone):
    return re.match(r"^\d{10}$", phone) is not None


class TestRegex(unittest.TestCase):
    def test_valid_phone(self):
        self.assertTrue(is_valid_phone("0912345678"))

    def test_too_short(self):
        self.assertFalse(is_valid_phone("12345"))

    def test_with_letters(self):
        self.assertFalse(is_valid_phone("12345abcde"))

    def test_too_long(self):
        self.assertFalse(is_valid_phone("1234567890123"))


if __name__ == "__main__":
    unittest.main()
