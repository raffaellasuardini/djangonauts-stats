from models import Author, PR, Issue, Results
from core.config import logger, OUTPUT_FILE
from core.github_client import load_prs, load_issues
from core.retrieve_data import get_djangonauts, get_repos
import datetime

djangonauts_dict = get_djangonauts()
repos = get_repos()


class DjangonautsReport:
    def __init__(self, start_date=None, end_date=None, output_file=OUTPUT_FILE):
        today = datetime.date.today()
        self.end_date = end_date or today
        self.start_date = start_date or (self.end_date - datetime.timedelta(days=7))
        self.output_file = output_file
        self.results = Results()

    def load_data(self):
        for repo in repos:
            logger.info(f"Loading data from {repo}")

            #load open pr
            for item in load_prs(repo, self.start_date, self.end_date, 'open'):
                author = self._create_author(item.get('author'))
                pr = self._create_pr(item, author)
                if author.login in djangonauts_dict.keys():
                    self.results.prs.append(pr)
            #load merged pr
            for item in load_prs(repo, self.start_date, self.end_date, 'merged'):
                author = self._create_author(item.get('author'))
                pr = self._create_pr(item, author)
                if author.login in djangonauts_dict.keys():
                    self.results.prs.append(pr)
            #load open issue
            for item in load_issues(repo, self.start_date, self.end_date):
                author = self._create_author(item.get('author'))
                issue = self._create_issue(item, author)
                if author.login in djangonauts_dict.keys():
                    self.results.issues.append(issue)

    def _create_author(self, raw_author):
        if not raw_author:
            return None
        return Author(
            login=raw_author.get("login", "").lower(),
            name=raw_author.get("name", ""),
        )

    def _create_pr(self, item, author):
        if not author or author.login not in djangonauts_dict.keys():
            return None
        if item.get('mergedAt'):
            merged_date = datetime.datetime.strptime(item.get('mergedAt').split("T")[0], "%Y-%m-%d").date()
        else:
            merged_date = None

        return PR(
            title=item["title"],
            number=item["number"],
            url=item["url"],
            author=author,
            created=datetime.datetime.strptime(item["createdAt"].split("T")[0], "%Y-%m-%d").date(),
            merged=merged_date,
            state=item['state']

        )

    def _create_issue(self, item, author):
        if not author or author.login not in djangonauts_dict.keys():
            return None
        return Issue(
            state=item["state"],
            title=item["title"],
            assignee=item.get("assignee"),
            author=author,
            url=item["url"],
            created=datetime.datetime.strptime(item["createdAt"].split("T")[0], "%Y-%m-%d").date(),
        )

    def export_report(self):
        prs = self.results.prs
        issues = self.results.issues

        pr_authors = self.results.get_pr_authors()
        djangonauts_prs_authors = [djangonauts_dict[author.login] for author in pr_authors]
        issue_authors = self.results.get_issue_authors()
        djangonauts_issues_authors = [djangonauts_dict[author.login] for author in issue_authors]

        nr_pr_open = self.results.count_open_prs()
        nr_pr_merged = self.results.count_merged_prs()
        nr_open_issue = self.results.count_open_issues()

        with open(self.output_file, "a", encoding="utf-8") as f:
            f.write(
                f"\n=== Djangonauts Report ({self.start_date} → {self.end_date}) ===\n"
                f"Open PRs: {nr_pr_open}, Merged: {nr_pr_merged}, Issue: {nr_open_issue}\n"
                f"Djangonaut Authors: {', '.join(author_name for author_name in djangonauts_prs_authors)}\n"
                f"{'\n--Merged--\n' if nr_pr_merged else ''}"
                f"{'\n\n'.join('🎉 ' + pr.title + '\n' + pr.author.name + '\n' + pr.url for pr in prs if pr.merged) if nr_pr_merged else '\n\nNo merged PRs\n'}"

                f"{'\n\n--Opened--\n' if nr_pr_open else ''}"
                f"{'\n\n'.join('✨ ' + pr.title + '\n' + pr.author.name + ' \n' + pr.url for pr in prs if pr.is_open()) if nr_pr_open else '\n\nNo opened PRs\n'}"

                f"{'\n--Issue--\n' if nr_open_issue else '\n\n--No Issue--\n\n'}"
                f" {'\n\n'.join('✏️ ' + i.title + '\n' + i.author.name + '\n' + i.url for i in issues) if nr_open_issue else ''}"
                "====================================\n"
            )

        logger.info(f"Report written to {self.output_file}")

    def run(self):
        self.load_data()
        self.export_report()
