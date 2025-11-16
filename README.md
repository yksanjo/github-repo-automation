# GitHub Repository Automation Tool

🚀 Automatically configure your GitHub repositories with descriptions, topics, and README badges. Perfect for when uploading repos from Cursor or setting up new projects.

## Features

- ✅ **Auto-detect project type** - Detects language, framework, and project characteristics
- ✅ **Smart badge generation** - Generates appropriate badges based on project type
- ✅ **Update repository description** - Set or update repository description
- ✅ **Add repository topics** - Automatically add relevant topics/tags
- ✅ **Update README badges** - Intelligently adds badges to existing README or creates new one
- ✅ **Config file support** - Use JSON config for custom settings
- ✅ **Dry-run mode** - Preview changes before applying

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/github-repo-automation.git
cd github-repo-automation

# Install dependencies
pip install requests
```

### Setup GitHub Token

1. Go to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Generate a new token with `repo` scope
3. Set it as environment variable:

```bash
export GITHUB_TOKEN=ghp_your_token_here
```

### Usage

```bash
# Basic usage
python3 github-repo-automation.py --repo owner/repo-name

# With custom description and topics
python3 github-repo-automation.py --repo owner/repo-name \
  --description "My awesome project" \
  --topics python,automation,cli

# Using config file
python3 github-repo-automation.py --repo owner/repo-name --config config.json

# Preview changes (dry-run)
python3 github-repo-automation.py --repo owner/repo-name --dry-run
```

## Badge Generation

The tool automatically generates badges based on your project:

- **License badge** (if license detected)
- **Language badge** (Python, JavaScript, TypeScript, Rust, Go, Java)
- **GitHub stats** (stars, forks, issues)
- **CI/CD badge** (if GitHub Actions detected)
- **Docker badge** (if Docker detected)
- **Last commit badge**
- **Custom badges** (from config)

## Configuration

Create a `config.json` file:

```json
{
  "description": "My awesome project description",
  "topics": ["python", "automation", "cli"],
  "custom_badges": [
    "[![Maintained](https://img.shields.io/badge/Maintained-yes-green.svg)](https://github.com/owner/repo)"
  ]
}
```

See `github-repo-automation.config.example.json` for a complete example.

## Examples

### Python Project

```bash
python3 github-repo-automation.py --repo myusername/my-python-tool \
  --description "A powerful Python CLI tool" \
  --topics python,cli,automation
```

### JavaScript/TypeScript Project

```bash
python3 github-repo-automation.py --repo myusername/my-js-app \
  --description "Modern web application" \
  --topics javascript,typescript,react,web
```

## Command Line Options

```
--repo REPO          Repository in format 'owner/repo' or full GitHub URL (required)
--token TOKEN        GitHub personal access token (or set GITHUB_TOKEN env var)
--description DESC   Repository description
--topics TOPICS      Comma-separated list of topics
--config PATH        Path to JSON configuration file
--badges-only        Only update badges, skip description and topics
--dry-run            Show what would be done without making changes
--branch BRANCH      Branch name (default: main)
```

## Requirements

- Python 3.6+
- `requests` library: `pip install requests`
- GitHub personal access token with `repo` scope

## Use Cases

### After Creating a Repo from Cursor

1. Create the repository on GitHub
2. Run the automation tool:
   ```bash
   python3 github-repo-automation.py --repo owner/repo-name
   ```
3. Done! Your repo now has professional badges, topics, and description.

### Batch Processing

Process multiple repositories:

```bash
#!/bin/bash
repos=(
  "owner/repo1"
  "owner/repo2"
  "owner/repo3"
)

for repo in "${repos[@]}"; do
  python3 github-repo-automation.py --repo "$repo" --config shared-config.json
done
```

## Troubleshooting

**Authentication failed**
- Check your GitHub token is valid
- Ensure token has `repo` scope

**Repository not found**
- Verify repo name format: `owner/repo-name`
- Check you have access to the repository

**README update failed**
- The tool will show badges to add manually
- Copy and paste them into your README.md

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Badge Resources

- [Shields.io](https://shields.io/) - Create custom badges
- [GitHub Badges](https://github.com/badges/shields) - Badge service

---

**Made with ❤️ for developers who want to automate their GitHub workflow**

