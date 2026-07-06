import logging

LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s %(message)s'
LOG_FILE = 'ml/chatbot/chatbot.log'


def configure_logger() -> logging.Logger:
    logger = logging.getLogger('revsense_chatbot')
    if not logger.handlers:
        handler = logging.FileHandler(LOG_FILE)
        formatter = logging.Formatter(LOG_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
