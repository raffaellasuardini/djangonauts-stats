import dataclasses
import typing
import datetime


@dataclasses.dataclass(frozen=True)
class Author:
    login: str
    name: str = dataclasses.field(default=None)


@dataclasses.dataclass
class PR:
    title: str
    number: str
    url: str
    author: Author
    state: str
    repo: str
    created: datetime.date = None
    merged: datetime.date = None

    def is_open(self) -> bool:
        return self.state == "open"

    def is_merged(self) -> bool:
        return bool(self.merged)

    def is_closed(self):
        return self.state == "closed" and not bool(self.merged)


@dataclasses.dataclass
class Issue:
    title: str
    state: str
    author: Author
    url: str
    repo: str
    created: datetime.date = None

    def is_open(self) -> bool:
        return self.state == 'open'

@dataclasses.dataclass
class Team:
    owner: str
    repos: list[dict]
    members: list[str]

@dataclasses.dataclass
class Results:
    prs: typing.List[PR] = dataclasses.field(default_factory=list)
    issues: typing.List[Issue] = dataclasses.field(default_factory=list)
    teams: typing.List[Team] = dataclasses.field(default_factory=list)
    _seen_pr_numbers: set[str] = dataclasses.field(default_factory=set)

    def add_pr(self, pr: PR) -> bool:
        """Add a PR to the list of PRs if it's not present"""
        if pr.number in self._seen_pr_numbers:
            return False
        self._seen_pr_numbers.add(pr.number)
        self.prs.append(pr)
        return True

    def get_open_prs(self) -> typing.List[PR]:
        return list(filter(lambda pr: pr.is_open(), self.prs))

    def get_merged_prs(self) -> typing.List[PR]:
        return list(filter(lambda pr: pr.is_merged(), self.prs))

    def get_closed_prs(self) -> typing.List[PR]:
        return list(filter(lambda pr: pr.is_closed(), self.prs))

    def get_open_issues(self) -> typing.List[Issue]:
        return list(filter(lambda issue: issue.is_open(), self.issues))

    def get_pr_authors(self) -> typing.List[Author]:
        return list(set(pr.author for pr in self.prs))

    def get_issue_authors(self) -> typing.List[Author]:
        return list(set(issue.author for issue in self.issues))

    def count_open_prs(self) -> int:
        return len(self.get_open_prs())

    def count_merged_prs(self) -> int:
        return len(self.get_merged_prs())

    def count_closed_prs(self) -> int:
        return len(self.get_closed_prs())

    def count_open_issues(self) -> int:
        return len(self.get_open_issues())
