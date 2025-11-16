#!/bin/bash
# Setup script for github-repo-automation repository

set -e

REPO_NAME="github-repo-automation"
CURRENT_DIR=$(pwd)

echo "🚀 Setting up $REPO_NAME repository..."

# Check if we're in the right directory
if [ ! -f "github-repo-automation.py" ]; then
    echo "❌ Error: github-repo-automation.py not found"
    echo "   Please run this script from the repository root directory"
    exit 1
fi

# Initialize git if not already initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git branch -M main
else
    echo "✅ Git repository already initialized"
fi

# Add all files
echo "📝 Adding files to git..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "ℹ️  No changes to commit"
else
    echo "💾 Creating initial commit..."
    git commit -m "Initial commit: GitHub Repository Automation Tool

- Auto-detect project type and generate badges
- Update repository description and topics
- Intelligently add badges to README
- Config file support
- Dry-run mode for preview"
fi

echo ""
echo "✅ Repository setup complete!"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Create a new repository on GitHub:"
echo "   https://github.com/new"
echo "   Repository name: $REPO_NAME"
echo "   Description: Automatically configure GitHub repositories with descriptions, topics, and badges"
echo "   Visibility: Public (or Private)"
echo "   DO NOT initialize with README, .gitignore, or license (we already have these)"
echo ""
echo "2. Add the remote and push:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/$REPO_NAME.git"
echo "   git push -u origin main"
echo ""
echo "3. (Optional) Use the tool itself to add badges:"
echo "   python3 github-repo-automation.py --repo YOUR_USERNAME/$REPO_NAME"
echo ""

