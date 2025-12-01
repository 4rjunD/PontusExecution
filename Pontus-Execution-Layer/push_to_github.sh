#!/bin/bash
# Script to push code to GitHub repository

set -e

echo "🚀 Pushing Pontus Routing to GitHub..."
echo ""

cd /Users/arjundixit/Downloads/PontusExecution

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
fi

# Check remote
if ! git remote | grep -q origin; then
    echo "🔗 Adding remote repository..."
    git remote add origin https://github.com/4rjunD/PontusExecution.git
else
    echo "✅ Remote already configured"
    git remote set-url origin https://github.com/4rjunD/PontusExecution.git
fi

# Add all files (respecting .gitignore)
echo "📝 Staging files..."
git add -A

# Check what will be committed
echo ""
echo "Files to be committed:"
git status --short | head -20
echo ""

# Commit
echo "💾 Committing changes..."
git commit -m "Initial commit: Complete routing engine with production features

Features:
- Routing engine with OR-Tools and CPLEX support
- Graph builder and pathfinding algorithms
- ArgMax decision layer for route selection
- API endpoints for route optimization
- Production features: CORS, rate limiting, authentication, logging
- Enhanced health checks
- Comprehensive test suite
- Complete documentation

Excludes CPLEX installation files as requested." || echo "⚠️  No changes to commit or commit already exists"

# Set branch to main
git branch -M main

# Push
echo ""
echo "📤 Pushing to GitHub..."
echo "⚠️  You may need to authenticate with GitHub"
git push -u origin main || {
    echo ""
    echo "❌ Push failed. This might be due to:"
    echo "   1. Authentication required (use GitHub CLI or personal access token)"
    echo "   2. Repository permissions"
    echo ""
    echo "To push manually:"
    echo "   git push -u origin main"
    echo ""
    echo "Or use GitHub CLI:"
    echo "   gh auth login"
    echo "   git push -u origin main"
}

echo ""
echo "✅ Done!"

