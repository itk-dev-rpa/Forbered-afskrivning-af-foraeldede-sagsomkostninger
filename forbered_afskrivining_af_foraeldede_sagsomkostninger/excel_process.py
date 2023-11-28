"""Read Excel files and extract cases for the SAP process."""
import datetime
from io import BytesIO
import warnings
import openpyxl

REMOVE_INDHOLDSART = ("BØVO", "EJEN", "BYGS", "BYGB", "MERE", "MERU", "BUMR" ,"PLAL", "PLFL", "KAAL","KAFL")

# suppress warnings from openpyxl. E.g. "Cell R13023 is marked as a date but the serial value -693596 is outside the limits for dates. The cell will be treated as an error."
warnings.filterwarnings("ignore", category=UserWarning)

def _load_excel_files(path):
    wb = openpyxl.load_workbook(path, read_only=True)
    print(f"loaded {path}")
    ws = wb.active
    rows = ws.values
    header_row = next(rows)
    rows = list(rows)  # convert to list, because generator cannot be pickled

    return {'rows': rows, 'header': header_row}

# pylint: disable=(too-many-branches)
def read_sheet(paths: list[str] | list[BytesIO]) -> list[tuple[str, str, str]]:
    """This method reads all Excel files and applies the "Alteryx" filtering steps described in the PDD section 5.2.
    The KMD restanceliste from KMD, is reduced to a list of (Aftale, Bilagsnummer, FP)

    Args:
        paths: path to all Excel file

    Returns:
        Filtered rows from the Excel files.
    """

    # Step 1: Merge files to one list of rows
    sheets = []
    for path in paths:
        sheets.append(_load_excel_files(path))

    header_row = sheets[0]['header']
    rows = []
    for sheet in sheets:
        rows.extend(sheet['rows'])
    del sheets

    hovedstole = []
    sagsomkostninger = []

    for row in rows:
        # Step 2: Delete rows where Medhæfter is not empty
        if row[header_row.index('Medhæfter')] is not None:
            continue

        # Step 3: Delete row if RIM Aftale is MO and RIM aftalestatus is 28
        if row[header_row.index('RIM Aftale')] == 'MO' and row[header_row.index('RIM aftalestatus')] == '28':
            continue


        # Step 5: Slet rækker hvor indholdsart er på listen (e.g. BØVO.)
        if row[header_row.index('Indholdsart')] in REMOVE_INDHOLDSART:
            continue

        # Step 6: Delete rows where Aftale type is not empty
        if row[header_row.index('Aftale type')] is not None:
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
    def _expirey_date_passed(row):
        date = row[header_row.index('Forældelsesdato')]
        if date is None:
            return False

        if date > datetime.datetime.today():
            return False

        return True

    sagsomkostninger = [row for row in sagsomkostninger if _expirey_date_passed(row)]

    # Step 13: Split rows with "Indholdsart" ['DAGI', 'DAG2', 'SFO2'] to special_content_type_rows and not_special[...]
    special_content_type_rows = []
    not_special_content_type_rows = []

    for row in sagsomkostninger:
        if row[header_row.index('Indholdsart')] in ['DAGI', 'DAG2', 'SFO2']:
            special_content_type_rows.append(row)
        else:
            not_special_content_type_rows.append(row)


    # Step 14: select sagsomkostninger and hovedstole. match FP and Aftale
    # create set of (FP,aftale) from hovedstole
    # pylint: disable-next=(consider-using-set-comprehension)
    unique = set((row[header_row.index('ForretnPartner')], row[header_row.index('Aftale')]) for row in hovedstole)
    # remove rows from sagsomkostninger that do not have matching (FP, aftale) i hovedstole.
    not_special_content_type_rows = [row for row in not_special_content_type_rows if
                        (row[header_row.index('ForretnPartner')], row[header_row.index('Aftale')]) not in unique]

    # Step 15: Combine lists
    not_special_content_type_rows.extend(special_content_type_rows)

    # Step 16: Delete rows where RIM Aftale == 'IN' and RIM aftalestatus == 21
    _sagsomkostninger = []
    for row in not_special_content_type_rows:
        if row[header_row.index('RIM Aftale')] == 'IN' and row[header_row.index('RIM aftalestatus')] == '21':
            continue
        _sagsomkostninger.append(row)

    not_special_content_type_rows = _sagsomkostninger

    # reduce to three rows: Aftale, Bilagsnummer, FP
    return [(row[header_row.index('Aftale')], row[header_row.index('Bilagsnummer')], row[header_row.index('ForretnPartner')]) for row in
            not_special_content_type_rows]
