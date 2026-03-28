import pandas as pd
import json
from core.config import logger


def get_djangonauts_from_file(file="data/djangonauts.csv") -> dict:
    """

    :param file:
    :return: a dictionary "login": "name"
    """
    try:
        df = pd.read_csv(file)
    except FileNotFoundError:
        logger.error(f"Djangonauts file not found: {file}")
        return {}
    except pd.errors.EmptyDataError:
        logger.error(f"Empty DataFrame found: {file}")
        return {}

    df.columns = [c.lower() for c in df.columns]
    if 'github username' not in df.columns or 'name' not in df.columns:
        logger.error("CSV missing required columns: 'github username' and 'name'")
        return {}

    login_list = [login.lower() for login in df['github username'].tolist()]
    name_list = [name.title() for name in df['name'].tolist()]
    djs = dict(zip(login_list, name_list))

    logger.info(f"Loaded {len(djs)} Djangonauts from {file}")
    return djs


def get_repos_from_file(file="data/repos.json") -> list:
    """

    :param file: default is data/repos.json
    :return: a list of dictionaries with three keys: owner (str), repos (list of str) and members (list of str)

    """
    try:
        with open(file) as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        logger.error(f"File not found: {file}")
        return []
    for entry in data:
        entry['members'] = [m.lower() for m in entry.get('members', [])]

    logger.info(f"Loaded {len(data)} repo configs from {file}")
    return data
