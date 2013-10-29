import logging
import logging.config


def configure_logging(config, disable_existing=False):
    """
    Set up (process-global!) loggers according to given app configuration.

    Look for 'logging' key in [app] config section, which should be the path to
    a logging config file in the format expected by logging.config.fileConfig.

    """
    logging_config = config.getpath('app.logging', None)
    if logging_config is not None:
        logging.config.fileConfig(
            logging_config, disable_existing_loggers=disable_existing)
