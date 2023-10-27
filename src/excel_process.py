import warnings
import datetime
import openpyxl

REMOVE_INDHOLDSART = ("BØVO", "EJEN", "BYGS", "BYGB", "MERE", "MERU", "BUMR")

# suppress warnings from openpyxl. E.g. "Cell R13023 is marked as a date but the serial value -693596 is outside the limits for dates. The cell will be treated as an error."
warnings.filterwarnings("ignore", category=UserWarning)


def read_sheet(path: str) -> list[tuple[str, str, str]]:
    """
    This method reads an Excel file and applies the "Alteryx" filtering steps described in the PDD section 5.2.
    The KMD restanceliste from KMD, is reduced to a list of (Aftale, Bilagsnummer, FP)

    Args:
        path: path to an Excel file

    Returns: Filtered rows from the Excel file.
    """

    wb = openpyxl.load_workbook(path, read_only=True)

    ws = wb.active
    rows = ws.values

    header_row = next(rows)
    
    hovedstole = []
    sagsomkostninger = []
    sag_indholdsart = []

    for row in rows:
        # Step 2: Delete rows where Medhæfter is not empty
        if row[header_row.index('Medhæfter')] != None:
            continue

        # Step 3: Delete row if RIM Aftale is MO and RIM aftalestatus is 28
        if row[header_row.index('RIM Aftale')] == 'MO' and row[header_row.index('RIM aftalestatus')] == '28':
            continue

        # Step 4: Delete rows where RIM Aftale == 'IN' and RIM aftalestatus == 21
        if row[header_row.index('RIM Aftale')] == 'IN' and row[header_row.index('RIM aftalestatus')] == '21':
            continue

        # Step 5: Slet rækker hvor indholdsart er på listen (e.g. BØVO.)
        if row[header_row.index('Indholdsart')] in REMOVE_INDHOLDSART:
            continue

        # Step 6: Delete rows where Aftale type is not empty
        if row[header_row.index('Aftale type')] != None:
            continue

        # Step 7: new lists

        # Step 8: Move rows with ZGBY or ZREN to sagsomkostninger
        if row[header_row.index('Hovedtransakt.')] in ('ZGBY', 'ZREN'):
            sagsomkostninger.append(row)
            continue

        # Step 9: Move rows with Ratespecifikation LRT to sagsomkostnigner.
        if row[header_row.index('Ratespecifikation')] == 'LRT':
            sagsomkostninger.append(row)
        else:  # Step 10: remaining rows, I.E. all, where Ratespecifikation is not LRT goes to hovedstole.
            hovedstole.append(row)

        # exit loop

    # Step 11: Delete row from sagsomkostninger if "RykkespærÅrsag" is 'N'.
    sagsomkostninger = [row for row in sagsomkostninger if row[header_row.index('RykkespærÅrsag')] != 'N']

    # Step 12: Delete row from sagsomkostninger if Forældelse is None or later than today.
    def _expirey_date_passed(date):
        if date == None:
            return False

        if date > datetime.datetime.today():
            return False

        return True

    sagsomkostninger = [row for row in sagsomkostninger if _expirey_date_passed(row[header_row.index('Forældelsesdato')])]

    # Step 13: Move rows with "Indholdsart" ['DAGI', 'DAG2', 'SFO2'] to sag_indholdsart
    index = 0
    while index < len(sagsomkostninger):
        if sagsomkostninger[index][header_row.index('Indholdsart')] in ['DAGI', 'DAG2', 'SFO2']:
            # remove row from sagsomkostninger
            sag_indholdsart.append(sagsomkostninger.pop(index))
        else:
            index += 1  # Move to the next item in the list
    # Step 14: select sagsomkostninger and hovedstole. match FP and Aftale
    # create set of (FP,aftale) from hovedstole
    right = set([(row[header_row.index('ForretnPartner')], row[header_row.index('Aftale')]) for row in hovedstole])
    # remove rows from sagsomkostninger that do not have matching (FP, aftale) i hovedstole.
    sagsomkostninger = [row for row in sagsomkostninger if
                        (row[header_row.index('ForretnPartner')], row[header_row.index('Aftale')]) not in right]

    # Step 15: Combine lists
    sagsomkostninger.extend(sag_indholdsart)

    wb.close()

    print(f"Done processing {path}.")

    # reduce to three rows: Aftale, Bilagsnummer, FP
    return [(row[header_row.index('Aftale')], row[header_row.index('Bilagsnummer')], row[header_row.index('ForretnPartner')]) for row in
            sagsomkostninger]


if __name__ == "__main__":
    """
    Load excel files from dir.
    Extract data from excel files and perform Alteryx steps.
    Merge results in a single file.
    """
    import multiprocessing
    import warnings
    import glob
    import time
    import openpyxl

    warnings.filterwarnings("ignore", category=UserWarning)
    PATH = r"C:\Users\az27355\Downloads\OneDrive_2023-09-06\Midlertidige filer"
    excel_files = glob.glob(f'{PATH}/*.xlsx')

    start = time.time()
    with multiprocessing.Pool(processes=8) as pool:
        results = pool.map(read_sheet, excel_files)

    sagsomkostninger = []
    for sheet in results:
        sagsomkostninger.extend(sheet)
    del results

    print(f"runtime {time.time() - start}. Rows:{len(sagsomkostninger)}")
