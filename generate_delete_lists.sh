#!/bin/bash

# Generate delete lists for GitHub organization cleanup

echo "Generating delete lists for yksanjo GitHub organization..."
echo ""

# Get all repositories
gh repo list yksanjo --limit 500 > all_repos.txt
TOTAL_REPOS=$(wc -l < all_repos.txt)
echo "Total repositories: $TOTAL_REPOS"

# Key projects to KEEP (from FINAL_ACTION_PLAN.md)
KEEP_PROJECTS=(
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
    "agent-recommender"
    "snow-globe-app"
    "ddsp-piano"
)

# Additional projects that might be worth keeping
ADDITIONAL_KEEP=(
    "agent-sandbox"
    "ghostly-memory-bank"
    "ghostly-core"
    "ghostly-cli"
    "mini-build-web"
    "mini-build-cli"
    "mini-build-game"
    "mini-build-your-own-x"
    "api-key-vault"
    "apihub"
    "complianceos-mvp"
    "dataswarm-platform"
    "moltworker"
    "death-of-saas"
    "llm-native-scrapers"
    "meowscope"
    "supplychain-viz"
    "stripe-devkit"
    "unified-scraper"
    "mcp-platform"
    "agent-platform"
)

# Combine all keep projects
ALL_KEEP=("${KEEP_PROJECTS[@]}" "${ADDITIONAL_KEEP[@]}")

# Create keep list file
echo "# Repositories to KEEP" > keep_repos.txt
for repo in "${ALL_KEEP[@]}"; do
    echo "$repo" >> keep_repos.txt
done

echo "Repositories to keep: ${#ALL_KEEP[@]}"
echo ""

# Extract just repository names from all_repos.txt
cut -f1 all_repos.txt | cut -d'/' -f2 > repo_names.txt

# Create delete list (repos not in keep list)
echo "# Repositories to DELETE" > delete_all_new.txt
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
        echo "$repo" >> delete_all_new.txt
    fi
done < repo_names.txt

DELETE_COUNT=$(wc -l < delete_all_new.txt)
echo "Repositories to delete: $DELETE_COUNT"
echo ""

# Create high confidence delete list (templates, examples, etc.)
echo "# High confidence deletions" > delete_high_confidence_new.txt
grep -i -E "(template|starter|boilerplate|example|demo|sample|test-|^test$|^demo$|^example$)" repo_names.txt >> delete_high_confidence_new.txt

# Add obvious forks
grep -i fork repo_names.txt >> delete_high_confidence_new.txt

# Add empty description repos (likely templates)
while IFS=$'\t' read -r full_name description; do
    repo=$(echo "$full_name" | cut -d'/' -f2)
    if [ -z "$description" ] || [ "$description" = "public" ] || [ "$description" = "private" ]; then
        echo "$repo" >> delete_high_confidence_new.txt
    fi
done < all_repos.txt

# Remove duplicates and sort
sort -u delete_high_confidence_new.txt > tmp.txt && mv tmp.txt delete_high_confidence_new.txt

HIGH_CONFIDENCE_COUNT=$(wc -l < delete_high_confidence_new.txt)
echo "High confidence deletions: $HIGH_CONFIDENCE_COUNT"
echo ""

# Show samples
echo "Sample of high confidence deletions (first 20):"
head -20 delete_high_confidence_new.txt
echo ""

echo "Summary:"
echo "Total repositories: $TOTAL_REPOS"
echo "To keep: ${#ALL_KEEP[@]}"
echo "To delete: $DELETE_COUNT"
echo "High confidence deletions: $HIGH_CONFIDENCE_COUNT"
echo ""
echo "Files created:"
echo "- keep_repos.txt (${#ALL_KEEP[@]} repos)"
echo "- delete_all_new.txt ($DELETE_COUNT repos)"
echo "- delete_high_confidence_new.txt ($HIGH_CONFIDENCE_COUNT repos)"
echo ""
echo "Next steps:"
echo "1. Review delete_high_confidence_new.txt"
echo "2. Run: ./delete_repos.sh delete_high_confidence_new.txt"
echo "3. Review remaining repositories"
echo "4. Polish kept repositories"