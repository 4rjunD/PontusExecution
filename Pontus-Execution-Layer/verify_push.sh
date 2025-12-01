#!/bin/bash
# Verify if push was successful

cd /Users/arjundixit/Downloads/PontusRouting

echo "🔍 Verifying GitHub push..."
echo ""

# Check if we can see remote branch
if git ls-remote --heads origin main 2>/dev/null | grep -q "refs/heads/main"; then
    echo "✅ Remote branch 'main' exists on GitHub"
    REMOTE_COMMIT=$(git ls-remote --heads origin main | cut -f1)
    LOCAL_COMMIT=$(git rev-parse HEAD)
    
    if [ "$REMOTE_COMMIT" = "$LOCAL_COMMIT" ]; then
        echo "✅ Local and remote commits match!"
        echo "✅ Push was successful!"
        echo ""
        echo "📍 Repository: https://github.com/4rjunD/PontusRouting"
    else
        echo "⚠️  Commits don't match - may need to push"
        echo "   Local:  $LOCAL_COMMIT"
        echo "   Remote: $REMOTE_COMMIT"
    fi
else
    echo "⚠️  Remote branch not found - push may have failed"
    echo "   Run: ./execute_push.sh to push"
fi

echo ""
echo "Current git status:"
git status --short | head -10

