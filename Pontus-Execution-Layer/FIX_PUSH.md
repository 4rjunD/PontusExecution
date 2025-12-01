# Fix Push Permission Error

The 403 error means the token doesn't have permission. Here are solutions:

## Solution 1: Check Token Permissions

Your token needs `repo` scope. To fix:

1. Go to: https://github.com/settings/tokens
2. Find your token or create a new one
3. Make sure it has `repo` scope checked
4. Use the new token

## Solution 2: Use GitHub CLI (Easiest)

```bash
cd /Users/arjundixit/Downloads/PontusRouting
gh auth login
git push -u origin main
```

## Solution 3: Use SSH (If you have SSH keys)

```bash
cd /Users/arjundixit/Downloads/PontusRouting
git remote set-url origin git@github.com:4rjunD/PontusRouting.git
git push -u origin main
```

## Solution 4: Generate New Token with Correct Permissions

1. Go to: https://github.com/settings/tokens/new
2. Name it: "Pontus Routing Push"
3. Select scope: **repo** (check the box)
4. Click "Generate token"
5. Copy the new token
6. Use it in the push command

