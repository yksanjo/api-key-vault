#!/bin/bash

# Create final delete list for GitHub organization cleanup

echo "Creating final delete list..."
echo ""

# Core projects to KEEP (20 projects with real commits)
CORE_PROJECTS=(
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
    "complianceos-mvp"
    "moltworker"
)

# Additional promising projects to KEEP (10 projects)
ADDITIONAL_KEEP=(
    "agent-sandbox"
    "ghostly-memory-bank"
    "ghostly-core"
    "ghostly-cli"
    "api-key-vault"
    "apihub"
    "mini-build-web"
    "mini-build-cli"
    "mini-build-game"
    "mini-build-your-own-x"
)

# Combine all keep projects
ALL_KEEP=("${CORE_PROJECTS[@]}" "${ADDITIONAL_KEEP[@]}")
echo "Total projects to keep: ${#ALL_KEEP[@]}"
echo ""

# Get all repositories
echo "Fetching all repositories..."
gh repo list yksanjo --limit 500 > all_repos_full.txt
TOTAL_REPOS=$(wc -l < all_repos_full.txt)
echo "Total repositories found: $TOTAL_REPOS"

# Extract repository names
cut -f1 all_repos_full.txt | cut -d'/' -f2 > all_repo_names.txt

# Create delete list (everything not in keep list)
echo "# FINAL DELETE LIST" > delete_final.txt
echo "# Keep only ${#ALL_KEEP[@]} projects, delete everything else" >> delete_final.txt
echo "# Generated: $(date)" >> delete_final.txt
echo "" >> delete_final.txt

echo "Creating delete list..."
while read repo; do
    # Check if repo is in keep list
    keep=0
    for keep_repo in "${ALL_KEEP[@]}"; do
        if [ "$repo" = "$keep_repo" ]; then
            keep=1
            break
        fi
    done
    
    if [ $keep -eq 0 ]; then
        echo "$repo" >> delete_final.txt
    fi
done < all_repo_names.txt

DELETE_COUNT=$(wc -l < delete_final.txt)
# Subtract 4 for the header lines
DELETE_COUNT=$((DELETE_COUNT - 4))

echo "Repositories to delete: $DELETE_COUNT"
echo "Repositories to keep: ${#ALL_KEEP[@]}"
echo ""

# Create keep list for reference
echo "# PROJECTS TO KEEP" > keep_final.txt
echo "# ${#ALL_KEEP[@]} projects with real commits" >> keep_final.txt
echo "# Generated: $(date)" >> keep_final.txt
echo "" >> keep_final.txt

for repo in "${CORE_PROJECTS[@]}"; do
    echo "$repo" >> keep_final.txt
done

echo "" >> keep_final.txt
echo "# Additional promising projects" >> keep_final.txt
for repo in "${ADDITIONAL_KEEP[@]}"; do
    echo "$repo" >> keep_final.txt
done

# Show samples
echo "Sample of repositories to DELETE (first 30):"
head -34 delete_final.txt | tail -30
echo ""

echo "Projects to KEEP:"
echo "================="
for repo in "${CORE_PROJECTS[@]}"; do
    echo "- $repo"
done
echo ""
echo "Additional promising projects:"
for repo in "${ADDITIONAL_KEEP[@]}"; do
    echo "- $repo"
done
echo ""

echo "Summary:"
echo "--------"
echo "Total repositories: $TOTAL_REPOS"
echo "To keep: ${#ALL_KEEP[@]}"
echo "To delete: $DELETE_COUNT"
echo ""
echo "Files created:"
echo "- delete_final.txt ($DELETE_COUNT repos)"
echo "- keep_final.txt (${#ALL_KEEP[@]} repos)"
echo ""
echo "Next steps:"
echo "1. Review delete_final.txt"
echo "2. Run: ./delete_repos.sh delete_final.txt"
echo "3. Polish the kept repositories"
echo ""
echo "Warning: This will delete $(echo "scale=1; $DELETE_COUNT*100/$TOTAL_REPOS" | bc)% of your repositories!"
echo "Make sure you have backups of any important code."