# Djangonauts Stats
A script that retrieve the Pull Request, created and merged and Issue created by Djangonauts.

# Installation 
1. This script uses the `gh` CLI to search and filter PRs and Issues. [Check the gh CLI installation instructions](https://github.com/sakhawy/django-news-pr-filter#:~:text=gh%20CLI%20installation%20instructions).
2. After installing `gh` authenticate with a Github host.
    ```bash
    gh auth login 
    ```
3. Create a venv :
   ```bash 
   python3 -m venv venv
   source venv/bin/activate
   ```
4. Install `uv` and then the dependency:
    ```bash
   pip install uv
   uv sync
   ```

# Usage
Run `python main.py` without any arguments to pull last week's PR and Issue. The script create a `OUT.txt` inside the data folder.

Example `OUT.txt`

```
=== Djangonauts Report (2024-06-24 → 2024-06-30) ===
Open PRs: 0, Merged: 1, Issue: 0
Djangonaut Authors: Raffaella Suardini

--Merged--
🎉 Added link to the discord server inside FAQ.
Raffaella
https://github.com/django/django/pull/18257

No opened PRs


--No Issue--

 ====================================
```

## Options
Options are available to choose the dates

```
usage: Djangonauts Statistics [-h] [-s START_DATE] [-e END_DATE] [-v]

Pulls info about the PRs open and merged and open Issue from last week.

options:
  -h, --help            show this help message and exit
  -s, --start_date START_DATE
                        Filters PRs and Issues starting from `start_date`.e.g. 2024-01-28
  -e, --end_date END_DATE
                        Filters PRs and Issues ending on `start_date`.e.g. 2024-01-28
  -v, --verbose

```


## File needed
The script needs 2 file inside the data folder: `djangonauts.csv` and `repos.json`

### djangonaut.csv
needs two arguments, Github username and Name. It's not case sensitive.

example:
```djangonaut.csv
Github username,Name
raffaellasuardini,Raffaella suardini
```

### repos.json
It's a list of 2 Keys "owner" and "repos". An owner can have multiple repositories. 
If you need to check all the repositories of a certain owner use "*".
```json
[
  {
    "owner": "django",
    "repos": ["django"]
  },
  {
    "owner": "wagtail",
    "repos": ["wagtail"]
  },
  {
    "owner": "django-commons",
    "repos": ["django-debug-toolbar"]
  },
  {
    "owner": "djangopackages",
    "repos": ["djangopackages"]
  },
  {
    "owner": "django-cms",
    "repos": ["*"]
  }
]
```





# Credits 
This script is inspired by [Django News PR Filter](https://github.com/sakhawy/django-news-pr-filter) ❤️