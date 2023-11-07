#coding: utf-8
import os
import unittest
import sys

sys.path.append(r'C:\Users\az27355\OneDrive - Aarhus kommune\pycharmProjects\Forbered-afskrivning-af-foraeldede-sagsomkostninger\src')

class DataSelection(unittest.TestCase):
    """
    KMD sends "restancelister" lists as 24-28 Excel files. These need to be filtered down to a list of citizens with outdated legal costs.

    Test the Excel data selection process. The purpose of this test is to ensure
    that all data rows are selected, in accordance with the alteryx process.
    """
    def test_data_process(self):
        from src.excel_process import read_sheet
        import multiprocessing
        import glob
        from src.auxiliary import get_fp_and_aftale_from_file


        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        xlsx_path = os.path.join(current_script_dir, 'data', 'excel')
        excel_files = glob.glob(f'{xlsx_path}/*.xlsx')

        # Step 1: read restancelister
        sagsomkostninger = read_sheet(excel_files)

        # Step 2: read rykkerspærre file
        sap_file = os.path.join(current_script_dir, 'data', 'rykkerspærre.txt')
        with open(str(sap_file)) as file:
            data = file.read()

        fp_aftale = get_fp_and_aftale_from_file(data)

        # Step 3: filter restancelister based on rykkerspærre
        reduced_sagsomkostninger = []

        for row in sagsomkostninger:
            restance_aftale = row[0]
            restance_fp = row[2]
            if restance_fp in fp_aftale.keys():
                if restance_aftale in fp_aftale[restance_fp]:
                    print(f"rykkerspærre: {row}")
                    continue  # the fp, aftale combo is in rykkerspærrer.

            reduced_sagsomkostninger.append(row)

        reduced_sagsomkostninger # final outcome

        self.assertEqual(1546, len(reduced_sagsomkostninger)) # row count

        #import json
        #with open(os.path.join(current_script_dir, 'data', 'expected_result.json')) as file:
        #    expected_result = json.loads(file.read())