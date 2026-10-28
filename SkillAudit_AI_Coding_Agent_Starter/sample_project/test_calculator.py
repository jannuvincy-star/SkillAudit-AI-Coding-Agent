import unittest
from calculator import add, average, divide, multiply, subtract

class CalculatorTests(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)

    def test_average(self):
        self.assertEqual(average([2, 4, 6]), 4)

    def test_divide(self):
        self.assertEqual(divide(8, 2), 4)

    def test_divide_by_zero(self):
        with self.assertRaises(ValueError):
            divide(5, 0)

    def test_average_empty(self):
        with self.assertRaises(ValueError):
            average([])

    def test_multiply(self):
        self.assertEqual(multiply(3, 4), 12)

    def test_subtract(self):
        self.assertEqual(subtract(9, 4), 5)

if __name__ == "__main__":
    unittest.main()
