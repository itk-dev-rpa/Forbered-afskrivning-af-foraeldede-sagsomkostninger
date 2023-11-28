"""This script is designed to run a business process using the OpenOrchestrator framework.
It initializes the orchestrator connection, retrieves constants,
and runs a process in a loop with error handling and retry mechanisms.

This script is designed to be executed as the main entry point for the automation process.
"""
import traceback
import sys
from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from forbered_afskrivining_af_foraeldede_sagsomkostninger import reset
from forbered_afskrivining_af_foraeldede_sagsomkostninger import error_screenshot
from forbered_afskrivining_af_foraeldede_sagsomkostninger import process
from forbered_afskrivining_af_foraeldede_sagsomkostninger import config
from forbered_afskrivining_af_foraeldede_sagsomkostninger.exceptions import BusinessError


def main():
    """OpenOrchestrator runs this method when a trigger is activated."""
    orchestrator_connection = OrchestratorConnection.create_connection_from_args()
    sys.excepthook = log_exception(orchestrator_connection)

    orchestrator_connection.log_trace("Process started.")

    orchestrator_connection.log_trace("Getting constants.")
    error_email = orchestrator_connection.get_constant(config.ERROR_EMAIL)

    error_count = 0
    for _ in range(config.MAX_RETRY_COUNT):
        try:
            orchestrator_connection.log_trace("Resetting.")
            reset.reset(orchestrator_connection)

            orchestrator_connection.log_trace("Running process.")
            process.process(orchestrator_connection)

            break

        except BusinessError as error:
            orchestrator_connection.log_error(f"BusinessError: {error}\nTrace: {traceback.format_exc()}")
            break

        except Exception as error:  # pylint: disable=broad-exception-caught
            error_count += 1
            error_type = type(error).__name__
            orchestrator_connection.log_error(f"Error caught during process. Number of errors caught: {error_count}. {error_type}: {error}\nTrace: {traceback.format_exc()}")
            error_screenshot.send_error_screenshot(error_email, error, orchestrator_connection.process_name)

    reset.kill_all()


def log_exception(orchestrator_connection: OrchestratorConnection) -> callable:
    """Catch unexpected exceptions."""
    def inner(type, value, traceback):  # pylint: disable=redefined-builtin, redefined-outer-name
        orchestrator_connection.log_error(f"Uncaught Exception:\nType: {type}\nValue: {value}\nTrace: {traceback}")
    return inner


if __name__ == '__main__':
    main()
