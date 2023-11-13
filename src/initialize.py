from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
import config
import pyodbc

def initialize(orchestrator_connection: OrchestratorConnection) -> None:
    """Create the job queue table if it does not exist
    """
    pass