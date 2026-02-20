#!/bin/bash

# Analyze commit history of repositories to determine which are original work

echo "Analyzing commit history for key repositories..."
echo ""

# List of repositories to analyze
REPOS_TO_ANALYZE=(
    "signal-based-recruitment"
    "agentchat"
    "coding-tutor-v2"
    "multi-agent-plugins"
    "Strudel-music-pattern-memory-bank"
    "coding-tutor"
    "beat-sensei"
    "linkedin-face-crm"
    "github-repo-agent"
    "deepseek-code-server"
    "agent-gym"
    "signalfox"
    "contextual-workspace"
    "agent-highway"
    "cli-manager-mcp"
    "vc-intelligence-mcp"
    "next-100-days"
    "snow-globe-app"
    "ddsp-piano"
    "agent-sandbox"
    "ghostly-memory-bank"
    "api-key-vault"
    "apihub"
    "complianceos-mvp"
    "moltworker"
)

echo "Repository analysis:"
echo "===================="

for repo in "${REPOS_TO_ANALYZE[@]}"; do
    echo -n "$repo: "
    
    # Check if repo exists locally
    if [ -d "$repo" ]; then
        # Get commit count
        cd "$repo"
        commit_count=$(git log --oneline 2>/dev/null | wc -l)
        cd ..
        
        # Get first commit date
        cd "$repo"
        first_commit=$(git log --reverse --format="%ad" --date=short 2>/dev/null | head -1)
        cd ..
        
        # Get last commit date
        cd "$repo"
        last_commit=$(git log --format="%ad" --date=short 2>/dev/null | head -1)
        cd ..
        
        echo "$commit_count commits | First: $first_commit | Last: $last_commit"
    else
        echo "Not found locally"
    fi
done

echo ""
echo "Checking for forks..."
echo "===================="

for repo in "${REPOS_TO_ANALYZE[@]}"; do
    echo -n "$repo: "
    
    # Check if it's a fork on GitHub
    if gh repo view "yksanjo/$repo" --json isFork 2>/dev/null | grep -q "true"; then
        echo "FORK"
    else
        echo "Original"
    fi
done