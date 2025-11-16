#!/usr/bin/env python3
"""
GitHub Repository Automation Tool
Automatically adds description, topics, and README badges to GitHub repositories.

Usage:
    python3 github-repo-automation.py --repo owner/repo-name
    python3 github-repo-automation.py --repo owner/repo-name --config config.json
    python3 github-repo-automation.py --repo owner/repo-name --description "My awesome project" --topics python,automation
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("❌ Error: 'requests' library is required. Install it with: pip install requests")
    sys.exit(1)


class GitHubRepoAutomation:
    """Automation tool for GitHub repository setup."""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None):
        """Initialize with GitHub token."""
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            print("⚠️  Warning: No GitHub token provided. Using unauthenticated API (limited rate limit)")
            print("   Set GITHUB_TOKEN environment variable or use --token flag")
        
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a request to GitHub API."""
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.request(method, url, headers=self.headers, **kwargs)
        
        if response.status_code == 401:
            raise Exception("❌ Authentication failed. Check your GitHub token.")
        elif response.status_code == 403:
            raise Exception("❌ Forbidden. Check token permissions or rate limit.")
        elif response.status_code == 404:
            raise Exception(f"❌ Repository not found: {endpoint}")
        
        response.raise_for_status()
        return response.json() if response.content else {}
    
    def get_repo_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository information."""
        return self._make_request("GET", f"/repos/{owner}/{repo}")
    
    def update_description(self, owner: str, repo: str, description: str) -> bool:
        """Update repository description."""
        try:
            self._make_request("PATCH", f"/repos/{owner}/{repo}", json={"description": description})
            print(f"✅ Updated description: {description}")
            return True
        except Exception as e:
            print(f"❌ Failed to update description: {e}")
            return False
    
    def update_topics(self, owner: str, repo: str, topics: List[str]) -> bool:
        """Update repository topics."""
        try:
            # GitHub API requires topics in a specific format
            self._make_request("PUT", f"/repos/{owner}/{repo}/topics", 
                             json={"names": topics},
                             headers={**self.headers, "Accept": "application/vnd.github.mercy-preview+json"})
            print(f"✅ Updated topics: {', '.join(topics)}")
            return True
        except Exception as e:
            print(f"❌ Failed to update topics: {e}")
            return False
    
    def get_readme(self, owner: str, repo: str, branch: str = "main") -> Optional[str]:
        """Get README content."""
        try:
            # Try common README filenames
            for filename in ["README.md", "readme.md", "Readme.md"]:
                try:
                    response = requests.get(
                        f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{filename}",
                        headers=self.headers
                    )
                    if response.status_code == 200:
                        return response.text
                except:
                    continue
            
            # Try GitHub API
            readme_data = self._make_request("GET", f"/repos/{owner}/{repo}/readme")
            import base64
            return base64.b64decode(readme_data["content"]).decode("utf-8")
        except:
            return None
    
    def update_readme(self, owner: str, repo: str, content: str, branch: str = "main", 
                     commit_message: str = "Add badges and update README") -> bool:
        """Update README file via GitHub API."""
        try:
            # Get current README SHA
            readme_data = self._make_request("GET", f"/repos/{owner}/{repo}/readme")
            sha = readme_data["sha"]
            
            # Encode content
            import base64
            encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
            
            # Update file
            self._make_request("PUT", f"/repos/{owner}/{repo}/contents/README.md", json={
                "message": commit_message,
                "content": encoded_content,
                "sha": sha,
                "branch": branch
            })
            print(f"✅ Updated README.md")
            return True
        except Exception as e:
            print(f"❌ Failed to update README: {e}")
            print(f"   Note: You may need to update README manually or ensure you have write access")
            return False


class BadgeGenerator:
    """Generate appropriate badges for a repository."""
    
    def __init__(self, owner: str, repo: str, repo_info: Dict[str, Any]):
        """Initialize with repository information."""
        self.owner = owner
        self.repo = repo
        self.repo_info = repo_info
        self.language = repo_info.get("language", "").lower()
        self.topics = repo_info.get("topics", [])
        self.license = repo_info.get("license", {}).get("key", "").lower() if repo_info.get("license") else ""
        self.default_branch = repo_info.get("default_branch", "main")
    
    def detect_project_type(self) -> Dict[str, Any]:
        """Detect project type based on language, topics, and files."""
        project_type = {
            "language": self.language,
            "is_python": self.language == "python",
            "is_javascript": self.language in ["javascript", "typescript"],
            "is_rust": self.language == "rust",
            "is_go": self.language == "go",
            "is_java": self.language == "java",
            "has_docker": "docker" in self.topics or "container" in self.topics,
            "has_ci": any(topic in self.topics for topic in ["ci", "github-actions", "travis", "circleci"]),
            "is_cli": "cli" in self.topics or "command-line" in self.topics,
            "is_api": "api" in self.topics or "rest" in self.topics or "graphql" in self.topics,
            "is_web": "web" in self.topics or "frontend" in self.topics or "react" in self.topics,
        }
        return project_type
    
    def generate_badges(self, custom_badges: Optional[List[str]] = None) -> List[str]:
        """Generate badges for the repository."""
        badges = []
        project_type = self.detect_project_type()
        
        # License badge
        if self.license:
            license_name = self.license.upper()
            if license_name == "MIT":
                badges.append(f'[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)')
            elif license_name == "APACHE-2.0":
                badges.append(f'[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)')
            elif license_name == "GPL-3.0":
                badges.append(f'[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)')
            else:
                badges.append(f'[![License](https://img.shields.io/badge/license-{license_name.replace("-", "%20")}-green.svg)](LICENSE)')
        
        # Language badges
        if project_type["is_python"]:
            badges.append('[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)')
        elif project_type["is_javascript"]:
            badges.append('[![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-yellow.svg)](https://www.javascript.com/)')
            if "typescript" in self.topics:
                badges.append('[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)')
        elif project_type["is_rust"]:
            badges.append('[![Rust](https://img.shields.io/badge/rust-1.70+-orange.svg)](https://www.rust-lang.org/)')
        elif project_type["is_go"]:
            badges.append('[![Go](https://img.shields.io/badge/go-1.20+-00ADD8.svg)](https://golang.org/)')
        elif project_type["is_java"]:
            badges.append('[![Java](https://img.shields.io/badge/java-11+-orange.svg)](https://www.java.com/)')
        
        # GitHub stats badges
        badges.append(f'[![GitHub stars](https://img.shields.io/github/stars/{self.owner}/{self.repo}?style=social)](https://github.com/{self.owner}/{self.repo}/stargazers)')
        badges.append(f'[![GitHub forks](https://img.shields.io/github/forks/{self.owner}/{self.repo}.svg)](https://github.com/{self.owner}/{self.repo}/network/members)')
        badges.append(f'[![GitHub issues](https://img.shields.io/github/issues/{self.owner}/{self.repo}.svg)](https://github.com/{self.owner}/{self.repo}/issues)')
        
        # CI/CD badges
        if project_type["has_ci"]:
            badges.append(f'[![CI](https://github.com/{self.owner}/{self.repo}/workflows/CI/badge.svg)](https://github.com/{self.owner}/{self.repo}/actions)')
        
        # Docker badge
        if project_type["has_docker"]:
            badges.append('[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)')
        
        # Last commit badge
        badges.append(f'[![Last commit](https://img.shields.io/github/last-commit/{self.owner}/{self.repo}.svg)](https://github.com/{self.owner}/{self.repo}/commits/{self.default_branch})')
        
        # Add custom badges
        if custom_badges:
            badges.extend(custom_badges)
        
        return badges
    
    @staticmethod
    def format_badge_section(badges: List[str]) -> str:
        """Format badges into a markdown section."""
        if not badges:
            return ""
        
        # Group badges in rows of 3-4 for better display
        badge_lines = []
        for i in range(0, len(badges), 4):
            badge_lines.append(" ".join(badges[i:i+4]))
        
        return "\n".join(badge_lines)


class ReadmeUpdater:
    """Update README with badges."""
    
    @staticmethod
    def add_badges_to_readme(readme_content: str, badges: List[str]) -> str:
        """Add badges to README, placing them after the title."""
        if not readme_content:
            # Create new README
            badge_section = BadgeGenerator.format_badge_section(badges)
            return f"# {badges[0] if badges else ''}\n\n{badge_section}\n\n"
        
        # Check if badges already exist
        if any("img.shields.io" in line for line in readme_content.split("\n")):
            print("ℹ️  Badges already exist in README. Skipping badge addition.")
            return readme_content
        
        # Find the title (first # heading)
        lines = readme_content.split("\n")
        title_index = -1
        for i, line in enumerate(lines):
            if line.startswith("# "):
                title_index = i
                break
        
        if title_index == -1:
            # No title found, add at the beginning
            badge_section = BadgeGenerator.format_badge_section(badges)
            return f"{badge_section}\n\n{readme_content}"
        
        # Insert badges after title
        badge_section = BadgeGenerator.format_badge_section(badges)
        lines.insert(title_index + 1, "")
        lines.insert(title_index + 2, badge_section)
        lines.insert(title_index + 3, "")
        
        return "\n".join(lines)


def parse_repo_url(repo_input: str) -> Tuple[str, str]:
    """Parse repository URL or owner/repo format."""
    # Handle full URL
    if "github.com" in repo_input:
        match = re.search(r"github\.com[/:]([^/]+)/([^/?#]+)", repo_input)
        if match:
            return match.group(1), match.group(2).rstrip("/")
    
    # Handle owner/repo format
    if "/" in repo_input:
        parts = repo_input.split("/")
        if len(parts) == 2:
            return parts[0], parts[1]
    
    raise ValueError(f"Invalid repository format: {repo_input}. Use 'owner/repo' or full GitHub URL")


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    with open(config_path, "r") as f:
        return json.load(f)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Automate GitHub repository setup: add description, topics, and badges",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python3 github-repo-automation.py --repo owner/repo-name
  
  # With custom description and topics
  python3 github-repo-automation.py --repo owner/repo-name \\
    --description "My awesome project" \\
    --topics python,automation,cli
  
  # Using config file
  python3 github-repo-automation.py --repo owner/repo-name --config config.json
  
  # Update only badges
  python3 github-repo-automation.py --repo owner/repo-name --badges-only
        """
    )
    
    parser.add_argument("--repo", required=True, help="Repository in format 'owner/repo' or full GitHub URL")
    parser.add_argument("--token", help="GitHub personal access token (or set GITHUB_TOKEN env var)")
    parser.add_argument("--description", help="Repository description")
    parser.add_argument("--topics", help="Comma-separated list of topics")
    parser.add_argument("--config", help="Path to JSON configuration file")
    parser.add_argument("--badges-only", action="store_true", help="Only update badges, skip description and topics")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--branch", default="main", help="Branch name (default: main)")
    
    args = parser.parse_args()
    
    # Parse repository
    try:
        owner, repo = parse_repo_url(args.repo)
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)
    
    print(f"🚀 GitHub Repository Automation Tool")
    print(f"📦 Repository: {owner}/{repo}\n")
    
    # Initialize GitHub client
    github = GitHubRepoAutomation(token=args.token)
    
    # Get repository info
    try:
        print("📡 Fetching repository information...")
        repo_info = github.get_repo_info(owner, repo)
        print(f"✅ Found repository: {repo_info.get('full_name')}")
        print(f"   Description: {repo_info.get('description') or '(none)'}")
        print(f"   Topics: {', '.join(repo_info.get('topics', [])) or '(none)'}")
        print(f"   Language: {repo_info.get('language') or '(none)'}\n")
    except Exception as e:
        print(f"❌ {e}")
        sys.exit(1)
    
    # Load config if provided
    config = {}
    if args.config:
        try:
            config = load_config(args.config)
            print(f"✅ Loaded configuration from {args.config}\n")
        except Exception as e:
            print(f"⚠️  Warning: Failed to load config: {e}\n")
    
    # Update description
    description = args.description or config.get("description")
    if description and not args.badges_only:
        if args.dry_run:
            print(f"🔍 [DRY RUN] Would update description: {description}")
        else:
            github.update_description(owner, repo, description)
    
    # Update topics
    topics = None
    if args.topics:
        topics = [t.strip() for t in args.topics.split(",")]
    elif config.get("topics"):
        topics = config["topics"]
    
    if topics and not args.badges_only:
        if args.dry_run:
            print(f"🔍 [DRY RUN] Would update topics: {', '.join(topics)}")
        else:
            github.update_topics(owner, repo, topics)
    
    # Generate and add badges
    print("\n🎨 Generating badges...")
    badge_gen = BadgeGenerator(owner, repo, repo_info)
    custom_badges = config.get("custom_badges", [])
    badges = badge_gen.generate_badges(custom_badges=custom_badges)
    print(f"✅ Generated {len(badges)} badges")
    
    # Get current README
    print("\n📄 Fetching README...")
    readme_content = github.get_readme(owner, repo, args.branch)
    if readme_content:
        print("✅ Found existing README")
    else:
        print("ℹ️  No README found, will create one")
    
    # Update README with badges
    if args.dry_run:
        print("\n🔍 [DRY RUN] Would update README with badges:")
        badge_section = BadgeGenerator.format_badge_section(badges)
        print(badge_section)
    else:
        updated_readme = ReadmeUpdater.add_badges_to_readme(readme_content or "", badges)
        
        # Only update if badges were added
        if updated_readme != readme_content:
            print("\n💾 Updating README...")
            success = github.update_readme(owner, repo, updated_readme, args.branch)
            if not success:
                print("\n💡 Tip: You can manually add these badges to your README:")
                print(BadgeGenerator.format_badge_section(badges))
        else:
            print("ℹ️  README already has badges, skipping update")
    
    print("\n✨ Done!")


if __name__ == "__main__":
    main()

