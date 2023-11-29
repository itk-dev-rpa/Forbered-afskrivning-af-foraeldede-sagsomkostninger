"""The main process where data is prepared and inserted in the queue."""
import os
import json
import io

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from itk_dev_shared_components.sap import multi_session
from itk_dev_shared_components.graph import authentication, mail
from forbered_afskrivining_af_foraeldede_sagsomkostninger.auxiliary import TemporaryFile, get_fp_and_aftale_from_file
from forbered_afskrivining_af_foraeldede_sagsomkostninger.excel_process import read_sheets
from forbered_afskrivining_af_foraeldede_sagsomkostninger import config
from forbered_afskrivining_af_foraeldede_sagsomkostninger.exceptions import BusinessError


def process(orchestrator_connection: OrchestratorConnection) -> None:
    """
    0. Establish Graph access
    1. GRAPH get emails
    2. Treat excel files according to alteryx rules
    3. Get rykkerspærre from SAP
    4. Filter excel output
    5. Insert results into job queue
    6. Delete emails
    """
    gc = orchestrator_connection.get_credential(config.GRAPH_CREDENTIALS)
    graph_access = authentication.authorize_by_username_password(username=gc.username, **json.loads(gc.password))

    # Step 1. GRAPH get emails
    attachment_bytes_list, kmd_emails = get_emails(orchestrator_connection, graph_access)

    # Step 2. Treat excel files according to alteryx rules
    sagsomkostninger = read_sheets(attachment_bytes_list)

    for att in attachment_bytes_list:
        att.close()

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
        if restance_fp in fp_aftale:
            if restance_aftale in fp_aftale[restance_fp]:
                continue  # Skip row: the fp, aftale combo is in rykkerspærrer.

        reduced_sagsomkostninger.append(row)  # row not in rykkerspærrer.

    # Step 5. Insert results into job queue.
    reference_list = [None]*len(reduced_sagsomkostninger)
    reduced_sagsomkostninger = [json.dumps(dict(zip(['aftale', 'bilagsnummer', 'fp'], row)))
                                for row in reduced_sagsomkostninger]
    orchestrator_connection.bulk_create_queue_elements(queue_name=config.QUEUE_NAME, data=reduced_sagsomkostninger,
                                                       references=reference_list)
    orchestrator_connection.log_trace(f"Inserted {len(reduced_sagsomkostninger)} job queue elements.")

    # Step 6. Delete emails.
    for email in kmd_emails:
        mail.delete_email(email, graph_access, permanent=False)
        orchestrator_connection.log_trace(f"Deleted email '{email.subject}' (received {email.received_time}).")


def get_sap_file_content() -> str:
    """Download rykkerspærre from SAP as a file and return content as a string.
    The file is automatically deleted.

    Returns:
            Rykkerspærre as a string.
    """
    session = multi_session.get_all_sap_sessions()[0]

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

    with open(str(tempfile), encoding='cp1252') as file:  # blocking until SAP is done writing
        data = file.read()
    return data


def get_emails(orchestrator_connection: OrchestratorConnection, graph_access: authentication.GraphAccess) -> tuple[list[io.BytesIO],list[mail.Email]]:
    """Search for emails from KMD and download attachments.
    Filter the emails to the ones with Excel restancelister attached.
    The expected file name format is '20231024RPA03_23_23.XLSX'->(date, name, file count, .XLSX).

    Returns:
        A tuple; lists of downloaded attachments and emails.

    Raises:
        BusinessError: When no emails were found.
        ValueError: When attachments are missing.
    """
    mails = mail.get_emails_from_folder('itk-rpa@mkb.aarhus.dk', 'Indbakke/Afskrivning af forældede sagsomkostninger', graph_access)

    kmd_mails = [email for email in mails if
                 email.has_attachments and email.subject.startswith('Liste til forældede sagsomkostninger') and email.sender == 'kan-ikke-besvares@kmd.dk']

    if not kmd_mails:
        raise BusinessError("No matching emails were found.")

    attachments = [mail.list_email_attachments(message, graph_access)[0] for message in kmd_mails]

    latest_file_date = sorted([att.name for att in attachments])[-1][:8]
    latest_attachments = [att.name for att in attachments if att.name.startswith(latest_file_date)]

    if len(latest_attachments) != latest_attachments[0][-7:-5]:
        raise ValueError(f"The number of attachments did not correspond with the number that is embedded in the filename. List of attached files: {latest_attachments}")

    orchestrator_connection.log_trace(f"Downloading {len(latest_attachments)} excel attachments with date {latest_file_date}.")
    attachment_bytes_list = [mail.get_attachment_data(attachment, graph_access) for attachment in attachments]

    return attachment_bytes_list, kmd_mails
