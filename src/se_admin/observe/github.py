"""GitHub observation - remote repo state via GitHub REST API.

No decisions, no side effects.  Returns plain facts.
Uses urllib.request to avoid adding a dependency.
"""

from dataclasses import dataclass
import json
import urllib.request

_API = "https://api.github.com"


def _urlopen(req: urllib.request.Request):  # noqa: S310
    return urllib.request.urlopen(req)  # noqa: S310


def _get(
    url: str, token: str, *, accept: str = "application/vnd.github+json"
) -> object:
    req = urllib.request.Request(  # noqa: S310
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": accept,
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with _urlopen(req) as resp:
        return json.loads(resp.read())


def get_repo_topics(owner: str, repo: str, token: str) -> list[str]:
    """Return the topic tags set on a GitHub repo."""
    url = f"{_API}/repos/{owner}/{repo}/topics"
    data = _get(url, token, accept="application/vnd.github.mercy-preview+json")
    assert isinstance(data, dict)
    return data.get("names", [])


@dataclass
class PullRequest:
    """Structured data for a GitHub pull request."""

    number: int
    title: str
    author: str
    head_ref: str
    mergeable_state: str | None
    checks_passing: bool | None


def list_open_prs(owner: str, repo: str, token: str) -> list[dict]:
    """Return all open pull requests for owner/repo."""
    url = f"{_API}/repos/{owner}/{repo}/pulls?state=open&per_page=100"
    data = _get(url, token)
    assert isinstance(data, list)
    return data


def list_dependabot_prs(owner: str, repo: str, token: str) -> list[dict]:
    """Return open PRs authored by dependabot[bot]."""
    prs = list_open_prs(owner, repo, token)
    return [pr for pr in prs if pr.get("user", {}).get("login") == "dependabot[bot]"]


def get_pr_check_status(owner: str, repo: str, ref: str, token: str) -> str | None:
    """Return combined check status for a ref: 'success' | 'failure' | 'pending' | None."""
    url = f"{_API}/repos/{owner}/{repo}/commits/{ref}/check-runs"
    data = _get(url, token)
    assert isinstance(data, dict)
    runs = data.get("check_runs", [])
    if not runs:
        return None
    statuses = {r["conclusion"] for r in runs if r.get("conclusion")}
    if "failure" in statuses or "cancelled" in statuses:
        return "failure"
    if all(r.get("conclusion") == "success" for r in runs):
        return "success"
    return "pending"
