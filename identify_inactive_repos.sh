#!/bin/bash

# Identify inactive or low-activity repositories

echo "Identifying inactive repositories..."
echo ""

# Get all repositories with their last push date
gh repo list yksanjo --limit 500 --json name,pushedAt > repos_with_dates.json

# Parse and analyze
echo "Repositories older than 30 days (inactive):"
echo "-------------------------------------------"

# Current date in ISO format
CURRENT_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Use jq to filter repositories older than 30 days
jq -r '.[] | select(.pushedAt < "'$(date -u -d "30 days ago" +"%Y-%m-%dT%H:%M:%SZ")'") | .name' repos_with_dates.json > inactive_repos.txt

INACTIVE_COUNT=$(wc -l < inactive_repos.txt)
echo "Found $INACTIVE_COUNT repositories inactive for 30+ days"
echo ""

# Show first 20
echo "First 20 inactive repositories:"
head -20 inactive_repos.txt
echo ""

# Also check for repositories with no description or empty description
echo "Repositories with poor descriptions:"
echo "------------------------------------"
gh repo list yksanjo --limit 500 | awk -F'\t' '{
    repo=$1;
    desc=$2;
    if (desc == "" || desc == "public" || desc == "private" || length(desc) < 20) {
        print repo;
    }
}' | cut -d'/' -f2 > poor_desc_repos.txt

POOR_DESC_COUNT=$(wc -l < poor_desc_repos.txt)
echo "Found $POOR_DESC_COUNT repositories with poor descriptions"
echo ""

# Show first 20
echo "First 20 repositories with poor descriptions:"
head -20 poor_desc_repos.txt
echo ""

# Combine for Phase 2 deletions
cat inactive_repos.txt poor_desc_repos.txt | sort -u > phase2_candidates.txt
PHASE2_COUNT=$(wc -l < phase2_candidates.txt)

echo "Phase 2 deletion candidates: $PHASE2_COUNT"
echo ""
echo "These repositories are either:"
echo "1. Inactive for 30+ days"
echo "2. Have poor/no description"
echo "3. Likely low-quality or abandoned"
echo ""
echo "Files created:"
echo "- inactive_repos.txt ($INACTIVE_COUNT repos)"
echo "- poor_desc_repos.txt ($POOR_DESC_COUNT repos)"
echo "- phase2_candidates.txt ($PHASE2_COUNT repos)"
echo ""
echo "Next steps:"
echo "1. Complete Phase 1 (delete templates)"
echo "2. Review phase2_candidates.txt"
echo "3. Delete obvious low-quality repos"
echo "4. Keep reviewing until you reach ~100 repos"