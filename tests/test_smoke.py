import importlib.util
from pathlib import Path

import pytest

# The module file name contains a hyphen, so load it explicitly.
_spec = importlib.util.spec_from_file_location(
    "gh_repo_automation",
    Path(__file__).resolve().parent.parent / "github-repo-automation.py",
)
gra = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gra)


def test_parse_owner_repo():
    assert gra.parse_repo_url("octocat/Hello-World") == ("octocat", "Hello-World")


def test_parse_full_url():
    assert gra.parse_repo_url("https://github.com/octocat/Hello-World") == (
        "octocat",
        "Hello-World",
    )


def test_parse_invalid_raises():
    with pytest.raises(ValueError):
        gra.parse_repo_url("not-a-repo")


def test_generate_badges_includes_license_and_stats():
    repo_info = {
        "language": "Python",
        "topics": ["cli", "ci"],
        "license": {"key": "mit"},
        "default_branch": "main",
    }
    gen = gra.BadgeGenerator("octocat", "Hello-World", repo_info)
    badges = gen.generate_badges()

    joined = "\n".join(badges)
    assert any("License-MIT" in b for b in badges)
    assert any("python-3" in b for b in badges)
    assert "img.shields.io/github/stars/octocat/Hello-World" in joined
    # CI topic present -> CI badge emitted.
    assert any("/workflows/CI/badge.svg" in b for b in badges)


def test_add_badges_after_title_and_idempotent():
    readme = "# My Project\n\nSome description.\n"
    badges = [
        "[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](x)"
    ]

    updated = gra.ReadmeUpdater.add_badges_to_readme(readme, badges)
    lines = updated.split("\n")
    assert lines[0] == "# My Project"
    assert "img.shields.io" in updated

    # Running again must not duplicate the badges.
    again = gra.ReadmeUpdater.add_badges_to_readme(updated, badges)
    assert again == updated
