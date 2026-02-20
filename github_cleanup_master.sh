#!/bin/bash

# Master script for GitHub organization cleanup

echo "=========================================="
echo "GITHUB ORGANIZATION CLEANUP MASTER PLAN"
echo "=========================================="
echo ""
echo "Current status: 500 repositories"
echo "Target: 30-50 high-quality repositories"
echo ""

# Function to show progress
show_progress() {
    CURRENT_COUNT=$(gh repo list yksanjo --limit 1 | wc -l)
    echo "📊 Current repository count: $CURRENT_COUNT"
    echo ""
}

# Initial progress
show_progress

echo "PHASE 1: Delete Obvious Templates & Demos"
echo "-----------------------------------------"
echo ""
echo "The following 13 repositories are templates/demos:"
cat phase1_delete.txt
echo ""
echo "These should be deleted first."
echo ""
read -p "Do you want to delete these 13 templates/demos? (y/n): " confirm1

if [ "$confirm1" = "y" ] || [ "$confirm1" = "Y" ]; then
    echo ""
    echo "🚀 Deleting Phase 1 repositories..."
    ./delete_repos.sh phase1_delete.txt
    echo ""
    show_progress
else
    echo "Skipping Phase 1 deletions."
fi

echo ""
echo "PHASE 2: Review Low-Quality Repositories"
echo "----------------------------------------"
echo ""
echo "Found 105 repositories with poor descriptions (likely low-quality)."
echo ""
echo "First 20:"
head -20 poor_desc_repos.txt
echo ""
echo "These repositories have empty or very short descriptions."
echo "They are likely auto-generated or low-quality."
echo ""
read -p "Do you want to see more details? (y/n): " confirm2

if [ "$confirm2" = "y" ] || [ "$confirm2" = "Y" ]; then
    echo ""
    echo "Full list of 105 repositories with poor descriptions:"
    cat poor_desc_repos.txt
    echo ""
fi

echo ""
echo "PHASE 3: Core Projects to KEEP"
echo "-------------------------------"
echo ""
echo "These 20 projects have real commits and are original work:"
echo ""
for i in {1..20}; do
    project=$(sed -n "${i}p" <(printf "%s\n" "signal-based-recruitment" "agentchat" "coding-tutor-v2" "multi-agent-plugins" "Strudel-music-pattern-memory-bank" "coding-tutor" "beat-sensei" "linkedin-face-crm" "github-repo-agent" "deepseek-code-server" "agent-gym" "signalfox" "contextual-workspace" "agent-highway" "cli-manager-mcp" "vc-intelligence-mcp" "next-100-days" "snow-globe-app" "complianceos-mvp" "moltworker"))
    echo "$i. $project"
done
echo ""
echo "These should definitely be kept and polished."
echo ""

echo "PHASE 4: Action Plan"
echo "--------------------"
echo ""
echo "Week 1 (Now):"
echo "  ✅ Delete 13 templates/demos (Phase 1)"
echo "  🔍 Review 105 poor-description repos"
echo "  🎯 Target: 500 → ~400 repositories"
echo ""
echo "Week 2:"
echo "  🔍 Review agent repositories (keep best 10-15)"
echo "  🔍 Review AI repositories (keep best 5-10)"
echo "  🗑️  Delete the rest"
echo "  🎯 Target: ~400 → ~100 repositories"
echo ""
echo "Week 3:"
echo "  🔍 Final review of all repositories"
echo "  ✅ Keep best 30-50 total"
echo "  🗑️  Delete everything else"
echo "  🎯 Target: ~100 → 30-50 repositories"
echo ""
echo "Week 4:"
echo "  📝 Polish READMEs for all kept repos"
echo "  🖼️  Add screenshots and documentation"
echo "  🌐 Create GitHub profile"
echo "  🔗 Update LinkedIn and other profiles"
echo ""

echo "IMMEDIATE NEXT STEPS"
echo "-------------------"
echo ""
echo "1. If you haven't already, delete Phase 1 templates:"
echo "   ./delete_repos.sh phase1_delete.txt"
echo ""
echo "2. Review poor-description repositories:"
echo "   cat poor_desc_repos.txt"
echo ""
echo "3. Start polishing your top 5 projects:"
echo "   cd signal-based-recruitment"
echo "   # Update README.md, add screenshots, etc."
echo ""
echo "4. Create a 'keep' list of repositories you want to preserve."
echo ""
echo "Remember the principles:"
echo "• Quality over quantity"
echo "• Keep only original work"
echo "• Document everything you keep"
echo "• Be honest about what you built"
echo ""
echo "Good luck with the cleanup! 🚀"