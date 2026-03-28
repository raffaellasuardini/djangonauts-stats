from github import Github

from models import Author, PR, Issue, Team, Results
from core.config import logger, OUTPUT_FILE, GITHUB_TOKEN
from core.github_client import get_prs, get_issues
from core.retrieve_data import get_djangonauts_from_file, get_repos_from_file
import datetime


class DjangonautsReport:
    def __init__(self, start_date=None, end_date=None, output_file=OUTPUT_FILE):
        today = datetime.date.today()
        self.djangonauts_dict = get_djangonauts_from_file()
        self.repos = get_repos_from_file()
        self.end_date = end_date or today
        self.start_date = start_date or (self.end_date - datetime.timedelta(days=7))
        self.output_file = output_file
        self.results = Results()
        self.create_teams(self.repos)

        token = GITHUB_TOKEN
        if not token:
            raise ValueError('GITHUB_TOKEN environment variable not set')
        self.github = Github(token)

    def create_teams(self, repos):
        for repo in repos:
            members = repo.get("members", [])
            team = Team(
                owner=repo['owner'],
                repos=repo['repos'],
                members=members,
            )
            logger.info(f"created team {team}")
            self.results.teams.append(team)

    def load_data_from_api(self):
        for team in self.results.teams:

            team_prs = get_prs(team, team.members, self.start_date, self.end_date, self.github)
            team_issues = get_issues(team, team.members, self.start_date, self.end_date, self.github)

            for item in team_prs:
                djangonaut_author = self._create_author(
                    login=item.user.login.lower(),
                    name=self.djangonauts_dict[item.user.login.lower()]
                )
                pr = self._create_pr(author=djangonaut_author, item=item)
                self.results.prs.append(pr)
                logger.info(f"Appended PR, total now: {len(self.results.prs)}")

            for item in team_issues:
                djangonaut_author = self._create_author(
                    login=item.user.login.lower(),
                    name=self.djangonauts_dict[item.user.login.lower()]
                )
                issue = self._create_issue(author=djangonaut_author, item=item)
                self.results.issues.append(issue)
                logger.info(f"Appended Issue, total now: {len(self.results.issues)}")

    def _create_author(self, login, name):
        return Author(
            login=login.lower(),
            name=name or "",
        )

    def _create_pr(self, item, author):
        merged_date = None
        if item.pull_request.merged_at:
            merged_date = item.pull_request.merged_at.date()

        repo = item.repository_url.split("/repos/")[1]

        pr = PR(
            title=item.title,
            number=item.number,
            url=item.html_url,
            author=author,
            repo=repo,
            created=item.created_at.date(),
            merged=merged_date,
            state=item.state

        )
        logger.info(f"Created PR: {pr.title} by {pr.author.login}")
        return pr

    def _create_issue(self, item, author):
        if not author or author.login not in self.djangonauts_dict.keys():
            return None

        repo = item.repository_url.split("/repos/")[1]

        return Issue(
            title=item.title,
            url=item.html_url,
            author=author,
            repo=repo,
            created=item.created_at.date(),
            state=item.state,
        )

    def export_report(self):
        prs = self.results.prs
        issues = self.results.issues

        pr_authors = self.results.get_pr_authors()
        djangonauts_prs_authors = [self.djangonauts_dict[author.login] for author in pr_authors]
        issue_authors = self.results.get_issue_authors()
        djangonauts_issues_authors = [self.djangonauts_dict[author.login] for author in issue_authors]

        nr_pr_open = self.results.count_open_prs()
        nr_pr_closed = self.results.count_closed_prs()
        nr_pr_merged = self.results.count_merged_prs()
        nr_open_issue = self.results.count_open_issues()

        with open(self.output_file, "a", encoding="utf-8") as f:
            f.write(
                f"\n=== Djangonauts Report ({self.start_date} → {self.end_date}) ===\n"
                f"Open PRs: {nr_pr_open}, Merged: {nr_pr_merged}, Closed: {nr_pr_closed} , Issue: {nr_open_issue}\n"
                f"Djangonaut Authors: {', '.join(author_name for author_name in djangonauts_prs_authors)}\n"
                f"{'\n--Merged--\n' if nr_pr_merged else ''}"
                f"{'\n\n'.join('🎉 ' + pr.repo + '\n' + pr.title + '\n' + pr.author.name + '\n' + pr.url for pr in prs if pr.merged) if nr_pr_merged else '\n\nNo merged PRs\n'}"

                f"{'\n\n--Opened--\n' if nr_pr_open else ''}"
                f"{'\n\n'.join('✨ ' + pr.repo + '\n' + pr.title + '\n' + pr.author.name + ' \n' + pr.url for pr in prs if pr.is_open()) if nr_pr_open else '\n\nNo opened PRs\n'}"

                f"{'\n\n--Closed--\n' if nr_pr_closed else ''}"
                f"{'\n\n'.join('🚧 ' + pr.repo + '\n' + pr.title + '\n' + pr.author.name + ' \n' + pr.url for pr in prs if pr.is_closed()) if nr_pr_closed else '\n\nNo closed PRs\n'}"

                f"{'\n\n--Issue--\n\n' if nr_open_issue else '\n\n--No Issue--\n\n'}"
                f"Djangonaut Authors: {', '.join(author_name for author_name in djangonauts_issues_authors)}\n"
                f" {'\n\n'.join('✏️ ' + i.repo + '\n' + i.title + '\n' + i.author.name + '\n' + i.url for i in issues) if nr_open_issue else ''}"
                "\n====================================\n"
            )

        logger.info(f"Report written to {self.output_file}")

    def run(self):
        self.load_data_from_api()
        self.export_report()
