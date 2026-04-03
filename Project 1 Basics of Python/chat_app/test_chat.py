import unittest
import os


def save_logic(filename, data):
    with open(filename, "w") as f:
        for entry in data:
            f.write(f"{entry['user']}:{entry['message']}\n")


def load_logic(filename):
    data = []
    with open(filename, "r") as f:
        for line in f:
            user, msg = line.strip().split(":", 1)
            data.append({"user": user, "message": msg})
    return data


class TestChatData(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_history.txt"
        self.sample_data = [{"user": "Tester", "message": "Hello World"}]

    def test_save_and_load(self):
        # 1. Test Saving
        save_logic(self.test_file, self.sample_data)
        self.assertTrue(os.path.exists(self.test_file))

        # 2. Test Loading
        loaded_data = load_logic(self.test_file)
        self.assertEqual(loaded_data[0]["user"], "Tester")
        self.assertEqual(loaded_data[0]["message"], "Hello World")

    def tearDown(self):
        # Clean up test file after running
        if os.path.exists(self.test_file):
            os.remove(self.test_file)


if __name__ == "__main__":
    unittest.main()
