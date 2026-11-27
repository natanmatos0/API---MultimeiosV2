import unittest
from unittest.mock import patch, MagicMock
from src.config import Config
from src import init_sentry
from app import app

class SentryIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_sentry_config_defaults(self):
        """Valida que as configurações padrão do Sentry foram carregadas corretamente."""
        self.assertIsInstance(Config.SENTRY_TRACES_SAMPLE_RATE, float)
        self.assertEqual(Config.SENTRY_TRACES_SAMPLE_RATE, 1.0)
        self.assertIsInstance(Config.SENTRY_PROFILE_SESSION_SAMPLE_RATE, float)
        self.assertEqual(Config.SENTRY_PROFILE_SESSION_SAMPLE_RATE, 1.0)
        self.assertEqual(Config.SENTRY_PROFILE_LIFECYCLE, "trace")

    @patch("src.sentry_sdk.init")
    @patch("src.sentry_sdk.is_initialized", return_value=False)
    def test_init_sentry_when_dsn_configured(self, mock_is_init, mock_sentry_init):
        """Valida que o Sentry é inicializado com Tracing e Profiling quando a DSN está preenchida."""
        with patch.object(Config, "SENTRY_DSN", "https://mockkey@o123456.ingest.sentry.io/123456"):
            init_sentry()
            mock_sentry_init.assert_called_once()
            _, kwargs = mock_sentry_init.call_args
            self.assertEqual(kwargs.get("dsn"), "https://mockkey@o123456.ingest.sentry.io/123456")
            self.assertEqual(kwargs.get("traces_sample_rate"), 1.0)
            self.assertEqual(kwargs.get("profile_session_sample_rate"), 1.0)
            self.assertEqual(kwargs.get("profile_lifecycle"), "trace")

    @patch("src.sentry_sdk.init")
    @patch("src.sentry_sdk.is_initialized", return_value=False)
    def test_init_sentry_when_dsn_empty(self, mock_is_init, mock_sentry_init):
        """Valida que o Sentry não é inicializado caso a DSN esteja em branco."""
        with patch.object(Config, "SENTRY_DSN", ""):
            init_sentry()
            mock_sentry_init.assert_not_called()

    def test_sentry_debug_route_triggers_500(self):
        """Valida que a rota de teste /sentry-debug dispara erro 500 para verificação."""
        response = self.client.get("/sentry-debug")
        self.assertEqual(response.status_code, 500)
        self.assertTrue(response.is_json)
        data = response.get_json()
        self.assertIn("erro", data)

if __name__ == "__main__":
    unittest.main()
