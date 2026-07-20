from unittest.mock import patch
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase
from psycopg2 import OperationalError as Psycopg2Error


# Używamy SimpleTestCase zamiast TestCase, bo nie chcemy w ogóle
# łączyć się z prawdziwą bazą danych podczas tego testu!
@patch("core.management.commands.wait_for_db.connections")
@patch("core.management.commands.wait_for_db.time.sleep")
class CommandTests(SimpleTestCase):

    def test_wait_for_db_ready(self, patched_sleep, patched_connections):
        """Test, że komenda kończy się od razu, gdy baza jest gotowa."""
        # Symulujemy, że kursor bazy danych działa od pierwszego strzału
        patched_connections["default"].cursor.return_value = True

        call_command("wait_for_db")

        # Sprawdzamy, czy próba połączenia nastąpiła dokładnie raz
        self.assertEqual(patched_connections["default"].cursor.call_count, 1)
        # Sprawdzamy, czy time.sleep NIE został wywołany
        patched_sleep.assert_not_called()

    def test_wait_for_db_delay(self, patched_sleep, patched_connections):
        """Test, że komenda czeka (sleep), gdy baza rzuca błąd OperationalError."""
        # Symulujemy, że baza rzuca 2 błędy psycopg2, potem 3 błędy Django,
        # a za 6. razem zwraca True (baza wstaje)
        patched_connections["default"].cursor.side_effect = [
            Psycopg2Error,
            Psycopg2Error,
            OperationalError,
            OperationalError,
            OperationalError,
            True,
        ]

        call_command("wait_for_db")

        # Sprawdzamy, czy komenda próbowała połączyć się 6 razy
        self.assertEqual(patched_connections["default"].cursor.call_count, 6)
        # Sprawdzamy, czy komenda uśpiła wiersz poleceń 5 razy (przed udaną próbą)
        self.assertEqual(patched_sleep.call_count, 5)
