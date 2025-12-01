#!/bin/bash
# Push with new token
# Usage: TOKEN=your_github_token ./push_with_new_token.sh

cd /Users/arjundixit/Downloads/PontusExecution

# Get token from environment variable or prompt
if [ -z "$TOKEN" ]; then
    echo "⚠️  No TOKEN environment variable set."
    echo "Usage: TOKEN=your_github_token ./push_with_new_token.sh"
    echo "Or set TOKEN in your environment first"
    exit 1
fi

echo "🚀 Pushing to GitHub with token..."
echo ""

# Set remote with token
git remote set-url origin "https://${TOKEN}@github.com/4rjunD/PontusExecution.git"

# Push
echo "📤 Executing push..."
if git push -u origin main 2>&1; then
    echo ""
    echo "✅ SUCCESS! Code pushed to GitHub"
    echo "📍 Repository: https://github.com/4rjunD/PontusExecution"
    echo ""
    
    # Remove token from URL
    git remote set-url origin "https://github.com/4rjunD/PontusExecution.git"
    echo "🔒 Token removed from git config for security"
    echo ""
    echo "✅ All done!"
else
    echo ""
    echo "❌ Push failed. Error above."
    exit 1
fi

