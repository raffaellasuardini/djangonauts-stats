from github import Github
from itertools import chain
from models import Author, PR, Issue, Team, Results
from core.config import logger, OUTPUT_FILE, GITHUB_TOKEN
from core.github_client import get_prs, get_issues
from core.retrieve_data import get_djangonauts_from_file, get_repos_from_file
import datetime


class DjangonautsReport:
    def __init__(self, start_date=None, end_date=None, closed_prs=False, output_file=OUTPUT_FILE):
        today = datetime.date.today()
        self.djangonauts_dict = get_djangonauts_from_file()
        self.repos = get_repos_from_file()
        self.end_date = end_date or today
        self.start_date = start_date or (self.end_date - datetime.timedelta(days=7))
        self.closed_prs = closed_prs
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

            team_prs = get_prs(team, team.members, self.start_date, self.end_date, self.github, is_merged=False)
            team_merged_prs = get_prs(team, team.members, self.start_date, self.end_date, self.github, is_merged=True)
            team_issues = get_issues(team, team.members, self.start_date, self.end_date, self.github)

            for item in chain(team_prs, team_merged_prs):
                djangonaut_author = self._create_author(
                    login=item.user.login.lower(),
                    name=self.djangonauts_dict[item.user.login.lower()]
                )
                pr = self._create_pr(author=djangonaut_author, item=item)
                added = self.results.add_pr(pr)
                if added:
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
        nr_issue = self.results.count_issues()

        with open(self.output_file, "a", encoding="utf-8") as f:

            lines = [f"\n=== Djangonauts Report ({self.start_date} → {self.end_date}) ===\n"]

            # Header
            closed_prs_string = ""
            if self.closed_prs:
                closed_prs_string = f", Closed: {nr_pr_closed}" if nr_pr_closed else ""

            lines.append(f"Open PRs: {nr_pr_open}, Merged: {nr_pr_merged}{closed_prs_string}, Issue: {nr_issue}")

            lines.append(
                f"Djangonaut Authors: {', '.join(djangonauts_prs_authors)}"
            )

            # --merged prs--
            if nr_pr_merged:
                lines.append(f"\n--Merged--\n")
                lines.append("\n\n".join(
                    f"🎉 {pr.repo}\n{pr.title}\n{pr.author.name}\n{pr.url}"
                    for pr in prs if pr.is_merged()
                ))
            else:
                lines.append(f"\n\nNo merged PRs\n")

            # -- opened prs--
            if nr_pr_open:
                lines.append(f"\n--Opened--\n")
                lines.append("\n\n".join(
                    f"✨{pr.repo}\n{pr.title}\n{pr.author.name}\n{pr.url}"
                    for pr in prs if pr.is_open()
                ))
            else:
                lines.append(f"\n\nNo opened PRs\n")

            # --closed prs--
            if self.closed_prs:
                if nr_pr_closed:
                    lines.append(f"\n--Closed--\n")
                    lines.append("\n\n".join(
                        f"🚧 {pr.repo}\n{pr.title}\n{pr.author.name}\n{pr.url}"
                        for pr in prs if pr.is_closed()
                    ))
                else:
                    lines.append("\n\nNo closed PRs\n")

            # --issues--
            if nr_issue:
                lines.append("\n\n--Issue--\n")
                lines.append(
                    f"Djangonaut Authors: {', '.join(djangonauts_issues_authors)}\n"
                )
                lines.append("\n\n".join(
                    f"✏️ {i.repo}\n{i.title}\n{i.author.name}\n{i.url}"
                    for i in issues
                ))
            else:
                lines.append("\n\n--No Issue--\n")

            # outro line

            lines.append("\n====================================\n")

            f.write("\n".join(lines))

        logger.info(f"Report written to {self.output_file}")

    def run(self):
        self.load_data_from_api()
        self.export_report()
