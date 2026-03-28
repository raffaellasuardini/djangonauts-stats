from core.config import logger


def from_list_to_string(team) -> str:
    if "*" in team.repos:
        return f"org:{team.owner}"
    return " ".join(f"repo:{team.owner}/{repo}" for repo in team.repos)


def get_prs(team, members: list[str], start_date, end_date, github):
    repos_string = from_list_to_string(team)
    members_str = " ".join(f"author:{m}" for m in members)
    query = f'{repos_string} {members_str} type:pr created:{start_date}..{end_date}'
    logger.info(f"Query: {query}")
    result = github.search_issues(query)
    logger.info(f"Found {result.totalCount} PRs for {team.owner}")
    return result


def get_issues(team, members: list[str], start_date, end_date, github):
    repos_string = from_list_to_string(team)
    members_str = " ".join(f"author:{m}" for m in members)
    query = f'{repos_string} {members_str} type:issue created:{start_date}..{end_date}'
    logger.info(f"Query: {query}")
    result = github.search_issues(query)
    logger.info(f"Found {result.totalCount} Issues for {team.owner}")
    return result