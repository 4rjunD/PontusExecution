#!/bin/bash
# Final push script with error handling

set -e

cd /Users/arjundixit/Downloads/PontusRouting

echo "🚀 Pushing Pontus Routing to GitHub..."
echo ""

# Initialize git if needed
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
fi

# Configure remote
echo "🔗 Configuring remote..."
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/4rjunD/PontusRouting.git 2>/dev/null || \
git remote set-url origin https://github.com/4rjunD/PontusRouting.git

# Add all files
echo "📝 Staging files..."
git add -A

# Show what will be committed
echo ""
echo "Files to be committed:"
git status --short | head -20
echo "..."

# Commit
echo ""
echo "💾 Committing..."
git commit -m "Complete routing engine ready for execution layer

Includes:
- Full routing engine (OR-Tools + CPLEX support)
- Graph builder and optimization solvers
- ArgMax decision layer for route selection
- All API endpoints for route optimization
- Production features: CORS, rate limiting, authentication, logging
- Enhanced health checks
- Complete data layer (Rishi's Part A)
- Comprehensive documentation including execution layer setup guide
- Test suites for verification
- All dependencies and configuration files

Ready for execution layer development (Part C)." || echo "⚠️  No changes to commit or already committed"

# Set branch
git branch -M main

# Push
echo ""
echo "📤 Pushing to GitHub..."
echo ""

# Try push
if git push -u origin main 2>&1; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo "📍 Repository: https://github.com/4rjunD/PontusRouting"
else
    echo ""
    echo "⚠️  Push failed. This usually means authentication is required."
    echo ""
    echo "To authenticate, run one of these:"
    echo ""
    echo "Option 1: GitHub CLI (recommended)"
    echo "  gh auth login"
    echo "  git push -u origin main"
    echo ""
    echo "Option 2: Personal Access Token"
    echo "  1. Go to: https://github.com/settings/tokens"
    echo "  2. Generate new token with 'repo' permissions"
    echo "  3. Use token as password when pushing:"
    echo "     git push -u origin main"
    echo ""
    echo "Option 3: SSH (if you have SSH keys set up)"
    echo "  git remote set-url origin git@github.com:4rjunD/PontusRouting.git"
    echo "  git push -u origin main"
    echo ""
    echo "Current status:"
    git status
fi

