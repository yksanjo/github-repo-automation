# github-repo-automation

A small command-line tool that configures a GitHub repository for you: it sets
the repository **description** and **topics**, detects the project type, and
injects an appropriate set of **README badges** (license, language, GitHub
stats, CI, Docker, last-commit) just below the title.

## Stack

Python 3, the GitHub REST API, and the [`requests`](https://pypi.org/project/requests/)
library (the only dependency).

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Authentication

Provide a GitHub personal access token with `repo` scope so the tool can update
the repository. Pass it with `--token` or set `GITHUB_TOKEN`:

```bash
export GITHUB_TOKEN=ghp_xxx
```

Without a token the tool runs read-only against the unauthenticated API (lower
rate limit) and cannot write changes.

## Usage

```bash
# Description + topics + badges from current repo metadata
python3 github-repo-automation.py --repo owner/repo-name

# Provide your own description and topics
python3 github-repo-automation.py --repo owner/repo-name \
  --description "My awesome project" \
  --topics python,automation,cli

# Drive everything from a config file
python3 github-repo-automation.py --repo owner/repo-name --config github-repo-automation.config.example.json

# Only refresh the README badges
python3 github-repo-automation.py --repo owner/repo-name --badges-only

# Preview changes without writing them
python3 github-repo-automation.py --repo owner/repo-name --dry-run
```

`--repo` accepts either `owner/repo` or a full GitHub URL. Use `--branch` to
target a branch other than `main`.

## Configuration file

A JSON file may supply `description`, `topics`, and `custom_badges`. See
`github-repo-automation.config.example.json` for the format.

## Repository structure

```text
github-repo-automation.py   # the CLI (API client, badge generator, README updater)
github-repo-automation.config.example.json
setup-repo.sh               # convenience wrapper
tests/                      # tests
requirements.txt            # requests
```
