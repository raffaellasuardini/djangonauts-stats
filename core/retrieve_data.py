import pandas as pd
import json
from core.config import logger
from core.github_client import load_repositories


def get_djangonauts(file="data/djangonauts.csv") -> dict:
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


def get_repos(file="data/repos.json") -> list:
    """

    :param file: default is data/repos.json
    :return: a list string for the repositories for example "django/django"
    """
    try:
        with open(file) as json_file:
            json_data = json.load(json_file)
    except FileNotFoundError:
        logger.error(f"File not found: {file}")
        return []

    repo_list = []
    for element in json_data:
        if len(element['repos']) <= 1:

            if element['repos'][0] == '*' or not element['repos'][0]:
                repo_list.extend(get_repos_from_owner(element['owner']))
            else:
                for repo in element['repos']:
                    repo_list.append(f"{element['owner']}/{repo}")

    return repo_list


def get_repos_from_owner(owner) -> list:
    """

    :param owner:
    :return: a list of owner/repo
    """
    response = load_repositories(owner)
    return [owner + "/" + item.pop('name') for item in response]
