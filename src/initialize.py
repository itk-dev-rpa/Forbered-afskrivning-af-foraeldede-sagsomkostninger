from OpenOrchestratorConnection.orchestrator_connection import OrchestratorConnection
import config
import pyodbc

def initialize(orchestrator_connection: OrchestratorConnection) -> None:
    """Create the job queue table if it does not exist
    """
    connection = pyodbc.connect(orchestrator_connection.get_constant(constant_name='Connection string'))
    with connection.cursor() as cursor:
        cursor.execute(f"IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{config.TABLE_NAME}') CREATE TABLE {config.TABLE_NAME} {config.CREATE_TABLE_QUERY}")
        # Commit the changes and close the connection
        connection.commit()
