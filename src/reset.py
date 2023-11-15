from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from itk_dev_shared_components.sap import sap_login

def reset(orchestrator_connection:OrchestratorConnection) -> None:
    """Clean up, close/kill all programs and start them again. """
    kill_all(orchestrator_connection)
    open_all(orchestrator_connection)

def clean_up(orchestrator_connection:OrchestratorConnection) -> None:
    """Do any cleanup needed to leave a blank slate."""
    pass

def close_all(orchestrator_connection:OrchestratorConnection) -> None:
    """Gracefully close all applications used by the robot."""
    pass

def kill_all(orchestrator_connection:OrchestratorConnection) -> None:
    """Forcefully close all applications used by the robot."""
    sap_login.kill_sap()
    pass

def open_all(orchestrator_connection:OrchestratorConnection) -> None:
    credentials = orchestrator_connection.get_credential("Anders SAP")
    sap_login.login_using_cli(credentials.username,credentials.password)
    pass
