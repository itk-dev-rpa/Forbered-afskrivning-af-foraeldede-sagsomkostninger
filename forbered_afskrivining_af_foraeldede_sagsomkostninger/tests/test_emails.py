"""Integration test of email attachment"""
import unittest
import os
from unittest.mock import MagicMock
from itk_dev_shared_components.graph import authentication
from forbered_afskrivining_af_foraeldede_sagsomkostninger.process import get_emails

class IntegrationTestEmails(unittest.TestCase):
    """Integration test of email attachment"""
    def test_get_emails(self):
        """Assert that file attachments are downloaded. This test requires files to be in the email inbox.
        Test passes if no exceptions are raised.
        No files are affected in the inbox, so no manual cleanup is required.
        """
        mock_open_rchestrator = MagicMock()
        graph_credentials = os.getenv("graph_credentials")

        graph_credentials = graph_credentials.split(',')
        username = graph_credentials[0]
        password = graph_credentials[1]
        client_id = graph_credentials[2]
        tenant_id = graph_credentials[3]
        graph_access = authentication.authorize_by_username_password(username,
                                                                     password,
                                                                     client_id=client_id,
                                                                     tenant_id=tenant_id)

        attachment_bytes_list, kmd_emails = get_emails(orchestrator_connection=mock_open_rchestrator, graph_access=graph_access)
        self.assertIsNotNone(attachment_bytes_list)
        self.assertIsNotNone(kmd_emails)

if __name__ == '__main__':
    unittest.main()
