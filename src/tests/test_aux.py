import unittest
import os


class TestAuxiliaryMethods(unittest.TestCase):
    def test_get_fp_and_aftale_from_file(self):
        from src.auxiliary import get_fp_and_aftale_from_file

        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        txt_path = os.path.join(current_script_dir, 'data', "temp.txt")

        with open(txt_path) as file:  # blocking until SAP is done writing
            data = file.read()

        aftale_fp = get_fp_and_aftale_from_file(data)

        # assert size
        self.assertEqual(2402, len(aftale_fp.keys()))
        self.assertEqual(3177, len([item for items in aftale_fp.values() for item in items])) # flatten the list of values

        # assert specific contents
        self.assertEqual(['86016'], aftale_fp['17621056'])
        self.assertEqual(['2363270', '2383524', '2389590', '2390836'], aftale_fp['147682'])

if __name__ == '__main__':
    unittest.main()

