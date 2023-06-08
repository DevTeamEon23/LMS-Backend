import random

from config.logconfig import logger


def sample_data(payload):
    logger.info(payload)
    return {
        "A":random.randint(100,1500),
    }