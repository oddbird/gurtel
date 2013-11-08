import mock

from gurtel import log
from gurtel.config import Config


class TestConfigureLogging(object):
    @mock.patch('logging.config.fileConfig')
    def test_logging(self, mock_fileConfig):
        """Configures logging if app.logging config key found."""
        log.configure_logging(Config({'app.logging': 'logging.ini'}))

        mock_fileConfig.assert_called_once_with(
            'logging.ini',
            disable_existing_loggers=False,
            )


    @mock.patch('logging.config.fileConfig')
    def test_no_logging(self, mock_fileConfig):
        """Does not configure logging if no config key found."""
        log.configure_logging(Config({}))

        assert mock_fileConfig.call_count == 0
