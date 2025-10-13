import os
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OUTPUT_FILE = os.path.join(BASE_DIR, 'data', 'OUT.txt')

logging.basicConfig(
    format='[%(asctime)s - %(name)s - %(levelname)s]: %(message)s'
)
logger = logging.getLogger('djangonauts')
logger.setLevel(logging.INFO)


def update_logger_level():
    logger.setLevel(logging.DEBUG)
