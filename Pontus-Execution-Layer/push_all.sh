#!/bin/bash
# Complete push script for Pontus Routing

set -e

REPO_DIR="/Users/arjundixit/Downloads/PontusRouting"
cd "$REPO_DIR"

echo "=========================================="
echo "🚀 Pushing Pontus Routing to GitHub"
echo "=========================================="
echo ""

# Step 1: Initialize git
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
fi

# Step 2: Configure remote
echo "🔗 Configuring remote repository..."
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/4rjunD/PontusRouting.git 2>/dev/null || \
    git remote set-url origin https://github.com/4rjunD/PontusRouting.git

echo "✅ Remote configured: $(git remote get-url origin)"
echo ""

# Step 3: Add all files
echo "📝 Staging all files..."
git add -A

# Count files
FILE_COUNT=$(git diff --cached --name-only | wc -l | tr -d ' ')
echo "✅ Staged $FILE_COUNT files"
echo ""

# Step 4: Commit
echo "💾 Creating commit..."
if git diff --cached --quiet; then
    echo "⚠️  No changes to commit (everything already committed)"
else
    git commit -m "Initial commit: Complete routing engine with production features

Features:
- Full routing engine (OR-Tools + CPLEX support)
- Graph builder and optimization solvers
- ArgMax decision layer for route selection
- All API endpoints for route optimization
- Production features: CORS, rate limiting, authentication, logging
- Enhanced health checks
- Complete data layer integration
- Comprehensive documentation including execution layer setup guide
- Test suites for verification
- All dependencies and configuration files

Ready for execution layer development (Part C)."
    echo "✅ Committed successfully"
fi
echo ""

# Step 5: Set branch
echo "🌿 Setting branch to main..."
git branch -M main
echo "✅ Branch set to main"
echo ""

# Step 6: Push
echo "📤 Pushing to GitHub..."
echo ""

if git push -u origin main 2>&1; then
    echo ""
    echo "=========================================="
    echo "✅ SUCCESS! Code pushed to GitHub"
    echo "=========================================="
    echo ""
    echo "📍 Repository: https://github.com/4rjunD/PontusRouting"
    echo "📊 Files pushed: $FILE_COUNT"
    echo ""
    echo "Your cofounder can now clone and start working on the execution layer!"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "⚠️  Push requires authentication"
    echo "=========================================="
    echo ""
    echo "Please authenticate using one of these methods:"
    echo ""
    echo "1. GitHub CLI (recommended):"
    echo "   gh auth login"
    echo "   git push -u origin main"
    echo ""
    echo "2. Personal Access Token:"
    echo "   - Go to: https://github.com/settings/tokens"
    echo "   - Generate token with 'repo' permissions"
    echo "   - Use as password: git push -u origin main"
    echo ""
    echo "3. SSH (if configured):"
    echo "   git remote set-url origin git@github.com:4rjunD/PontusRouting.git"
    echo "   git push -u origin main"
    echo ""
    exit 1
fi

