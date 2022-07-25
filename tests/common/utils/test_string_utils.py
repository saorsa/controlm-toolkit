import random
import unittest
from corelib.utils import generate_random_string


class StringUtilsTestCase(unittest.TestCase):

    def test_random_string(self):
        str_len = random.randrange(5, 50)
        random_string = generate_random_string(str_len)

        self.assertIsNotNone(random_string)
        self.assertEqual(len(random_string), str_len)

    def test_random_string_characters(self):
        random_string = generate_random_string(2000, 'A')

        self.assertIsNotNone(random_string)
        for c in random_string:
            assert c == 'A'


if __name__ == '__main__':
    unittest.main()
