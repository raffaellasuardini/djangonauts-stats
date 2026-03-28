import os
import logging
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OUTPUT_FILE = os.path.join(BASE_DIR, 'data', 'OUT.txt')

load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))

GITHUB_TOKEN = os.environ.get('GH_TOKEN')

logging.basicConfig(
    format='[%(asctime)s - %(name)s - %(levelname)s]: %(message)s'
)
logger = logging.getLogger('djangonauts')
logger.setLevel(logging.INFO)


def update_logger_level():
    logger.setLevel(logging.DEBUG)
