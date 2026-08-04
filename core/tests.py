from unittest.mock import patch
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase
from psycopg2 import OperationalError as Psycopg2Error


@patch("core.management.commands.wait_for_db.connections")
@patch("core.management.commands.wait_for_db.time.sleep")
class CommandTests(SimpleTestCase):

    def test_wait_for_db_ready(self, patched_sleep, patched_connections):
        patched_connections["default"].cursor.return_value = True

        call_command("wait_for_db")

        self.assertEqual(patched_connections["default"].cursor.call_count, 1)
        patched_sleep.assert_not_called()

    def test_wait_for_db_delay(self, patched_sleep, patched_connections):

        patched_connections["default"].cursor.side_effect = [
            Psycopg2Error,
            Psycopg2Error,
            OperationalError,
            OperationalError,
            OperationalError,
            True,
        ]

        call_command("wait_for_db")

        self.assertEqual(patched_connections["default"].cursor.call_count, 6)

        self.assertEqual(patched_sleep.call_count, 5)
