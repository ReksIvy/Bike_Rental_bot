import logging
import os

def log(file: str, message: str, level: int):
    """
    Custom logging function

    :param file: Log filename
    :param message: Log message
    :param level: Logging level (DEBUG=10, INFO=20, WARNING=30, ERROR=40, CRITICAL=50)
    """

    path = os.path.dirname(file)

    if path and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    
    logger = logging.getLogger(file)

    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(file)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)

    logger.log(level, message)