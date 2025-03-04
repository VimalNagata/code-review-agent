import unittest
from src.main import main

class TestMain(unittest.TestCase):
    def test_main(self):
        # Since main() just prints, we're just testing that it runs without errors
        try:
            main()
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"main() raised {type(e).__name__} unexpectedly: {e}")

if __name__ == "__main__":
    unittest.main()