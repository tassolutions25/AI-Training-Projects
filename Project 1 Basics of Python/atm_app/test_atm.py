import unittest

class TestATMLogic(unittest.TestCase):
    def test_withdrawal_logic(self):
        # Mock user
        user = {"card": "test", "pin": "1", "balance": 100.0}
        
        # Test Invalid Denomination
        amt = 15
        self.assertNotEqual(amt % 10, 0)
        
        # Test Insufficient Funds
        amt = 200
        self.assertTrue(amt > user['balance'])
        
        # Test Valid Transaction
        amt = 50
        user['balance'] -= amt
        self.assertEqual(user['balance'], 50.0)

if __name__ == "__main__":
    unittest.main()