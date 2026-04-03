import unittest
import re

# --- FUNCTIONS TO TEST (Copied from the main app logic) ---


def is_valid_eth_phone(phone):
    pattern = r"^(\+2519|\+2517|09|07)\d{8}$"
    return re.match(pattern, phone) is not None


users = []
transactions = []
current_user = None


def register_user(name, phone):
    if not is_valid_eth_phone(phone):
        return "Invalid format"
    for u in users:
        if u["phone"] == phone:
            return "Exists"
    users.append({"name": name, "phone": phone, "balance": 1000.0})
    return "Success"


def send_money(sender_phone, receiver_phone, amount):
    # Find sender and receiver in the list
    sender = next((u for u in users if u["phone"] == sender_phone), None)
    receiver = next((u for u in users if u["phone"] == receiver_phone), None)

    if not is_valid_eth_phone(receiver_phone):
        return "Invalid receiver phone format"
    if not sender or sender["balance"] < amount:
        return "Insufficient funds"
    if not receiver:
        return "Receiver not found"

    sender["balance"] -= amount
    receiver["balance"] += amount
    return "Success"


class TestEthiopianWallet(unittest.TestCase):

    def setUp(self):
        """Reset the data before every single test."""
        global users, transactions
        users = [
            {"name": "Alice", "phone": "0911223344", "balance": 1000.0},
            {"name": "Bob", "phone": "0711223344", "balance": 500.0},
        ]
        transactions = []

    # 1. TEST REGEX (Ethiopian Format)
    def test_phone_validation(self):
        # Valid Formats
        self.assertTrue(is_valid_eth_phone("0912345678"), "Should accept 09 local")
        self.assertTrue(is_valid_eth_phone("0712345678"), "Should accept 07 local")
        self.assertTrue(
            is_valid_eth_phone("+251912345678"), "Should accept +2519 international"
        )
        self.assertTrue(
            is_valid_eth_phone("+251712345678"), "Should accept +2517 international"
        )

        # Invalid Formats
        self.assertFalse(is_valid_eth_phone("0812345678"), "Should reject 08 prefix")
        self.assertFalse(is_valid_eth_phone("0912345"), "Should reject too short")
        self.assertFalse(is_valid_eth_phone("091234567899"), "Should reject too long")
        self.assertFalse(is_valid_eth_phone("abcdefghij"), "Should reject alphabets")

    # 2. TEST REGISTRATION
    def test_registration(self):
        # Register valid new user
        result = register_user("Charlie", "0955667788")
        self.assertEqual(result, "Success")
        self.assertEqual(len(users), 3)

        # Register duplicate phone
        result = register_user("Dave", "0911223344")
        self.assertEqual(result, "Exists")

        # Register invalid phone format
        result = register_user("Dave", "12345")
        self.assertEqual(result, "Invalid format")

    # 3. TEST MONEY TRANSFER
    def test_transfer_logic(self):
        # Valid transfer: Alice sends 200 to Bob
        result = send_money("0911223344", "0711223344", 200.0)
        self.assertEqual(result, "Success")

        # Verify balances
        alice = next(u for u in users if u["name"] == "Alice")
        bob = next(u for u in users if u["name"] == "Bob")
        self.assertEqual(alice["balance"], 800.0)
        self.assertEqual(bob["balance"], 700.0)

    def test_transfer_failures(self):
        # Insufficient funds
        result = send_money("0911223344", "0711223344", 5000.0)
        self.assertEqual(result, "Insufficient funds")

        # Receiver doesn't exist
        result = send_money("0911223344", "0900000000", 10.0)
        self.assertEqual(result, "Receiver not found")

        # Invalid receiver phone format
        result = send_money("0911223344", "999", 10.0)
        self.assertEqual(result, "Invalid receiver phone format")


if __name__ == "__main__":
    unittest.main()
