from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
import json


class Constants:
    """Define your constants."""
    def __init__(self):
        self.error_email = None
        self.graph_credentials = None


def get_constants(orchestrator_connection: OrchestratorConnection) -> Constants:
    """Get all constants used by the robot."""
    constants = Constants()

    # Get email address to send error screenshots to
    constants.error_email = orchestrator_connection.get_constant("Error Email")
    constants.graph_credentials = orchestrator_connection.get_credential("graph api")

    return constants
