from core.utils import send_command
from core.config import logger


def load_repositories(organization: str):
    logger.info(f'Loading repositories from org: {organization}')
    command = f'gh repo list {organization} --json name'
    return send_command(command)


def load_prs(repo: str, start_date, end_date, event):
    searches = {
        "created": f"is:pr created:{start_date}..{end_date}",
        "merged": f"is:pr merged:{start_date}..{end_date}",
        "closed": f"is:pr closed:{start_date}..{end_date}",
    }

    states= {
        "created": "all",
        "merged": "merged",
        "closed": "closed"
    }

    search = searches[event]
    state = states[event]
    command = (f'gh pr list -S "{search}" --repo {repo} --state {state} '
               f'--json title,number,url,author,createdAt,closedAt,mergedAt,state')
    return send_command(command)


def load_issues(repo: str, start_date, end_date):
    command = (f'gh issue list -S "created:{start_date}..{end_date}" --repo {repo} '
               f' --json title,assignees,url,state,author,createdAt')
    return send_command(command)
