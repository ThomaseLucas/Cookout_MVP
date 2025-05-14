import logging

# setup logging
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"


def setup_logger():
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    return logging.getLogger(__name__)


logger = setup_logger()