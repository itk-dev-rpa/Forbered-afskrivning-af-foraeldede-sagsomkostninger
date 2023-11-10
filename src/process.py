import glob
import os
from tempfile import TemporaryDirectory
from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from ITK_dev_shared_components.SAP import multi_session
from auxiliary import TemporaryFile, get_fp_and_aftale_from_file
from excel_process import read_sheet
from sql_transactions import Database
import config


def process(orchestrator_connection: OrchestratorConnection) -> None:

    """
    0. Initialize database connection
    1. GRAPH get emails
    2. Treat excel files according to alteryx rules
    3. Get rykkerspærre from SAP
    4. Filter excel output
    5. Insert results into job queue.
    """
    # Step 0. Connect to database
    db = Database(table_name=config.TABLE_NAME, connection_string='Driver={ODBC Driver 17 for SQL Server};Server=SRVSQLHOTEL03;Database=MKB-ITK-RPA;Trusted_Connection=yes;')
    # TODO Step 1. GRAPH get emails

    # Step 2. Treat excel files according to alteryx rules
    # TODO make temp dir and delete it when done.
    with TemporaryDirectory() as temp_dir:
        # save excel files here
        # graph.save.files.here(temp_dir)
        print("warning. importing files from hard coded path.")
        temp_dir = r"C:\Users\az27355\Downloads\restancelister_20231024\Midlertidige filer"  # TODO DELETE

        # get list of file paths from glob
        excel_files = glob.glob(f'{temp_dir}/*.xlsx')

        sagsomkostninger = read_sheet(excel_files)

    # tempdir is deleted.

    # Step 3. Get rykkerspærre from SAP
    file_content = get_sap_file_content()
    # get rykkerspærre
    fp_aftale = get_fp_and_aftale_from_file(file_content)

    # Step 4. Filter excel output
    # delete row from sagsomkostninger of fp and aftale is in rykkersprre dict.
    reduced_sagsomkostninger = []

    for row in sagsomkostninger:
        restance_aftale = row[0]
        restance_fp = row[2]
        if restance_fp in fp_aftale.keys():
            if restance_aftale in fp_aftale[restance_fp]:
                continue  # Skip row: the fp, aftale combo is in rykkerspærrer.

        reduced_sagsomkostninger.append(row)  # row not in rykkerspærrer.

    # Step 5. Insert results into job queue.
    db.insert_many_rows(reduced_sagsomkostninger)


def get_sap_file_content() -> str:
    session = multi_session.get_all_SAP_sessions()[0]
    """
    Download rykkerspærre from SAP as a file and return content as a string.
    The file is automatically deleted.                    
    """

    session.startTransaction("fplka")
    # set spærType = 51
    session.findById('/app/con[0]/ses[0]/wnd[0]/usr/ctxtS_LOTYP-LOW').text = '51'

    # send key F8
    session.findById('wnd[0]').sendVKey(8)

    # navigate menu bar to List -> Save/Send -> File...
    session.findById("wnd[0]/mbar/menu[0]/menu[1]/menu[2]").select()

    # select Regneark
    session.findById(
        "/app/con[0]/ses[0]/wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").select()

    session.findById('wnd[0]').sendVKey(0)  # Press Enter

    # create temporary file to hold data
    tempfile = TemporaryFile()

    # enter filename, filepath
    session.findById('/app/con[0]/ses[0]/wnd[1]/usr/ctxtDY_PATH').text = os.path.dirname(str(tempfile))
    session.findById('/app/con[0]/ses[0]/wnd[1]/usr/ctxtDY_FILENAME').text = os.path.basename(str(tempfile))

    # save data to file
    session.findById('/app/con[0]/ses[0]/wnd[1]/tbar[0]/btn[11]').press()

    with open(str(tempfile)) as file:  # blocking until SAP is done writing
        data = file.read()
    return data
