#!/bin/bash

# Start the GitHub organization cleanup process

echo "=========================================="
echo "🚀 GITHUB ORGANIZATION CLEANUP"
echo "=========================================="
echo ""
echo "Current status: 500 repositories"
echo "Target: 20-30 high-quality repositories"
echo ""

echo "Step 1: Review high priority deletions"
echo "----------------------------------------"
echo "High priority deletions (23 repos):"
cat delete_high_priority.txt
echo ""

read -p "Do you want to delete these 23 templates/forks? (y/n): " confirm1

if [ "$confirm1" = "y" ] || [ "$confirm1" = "Y" ]; then
    echo ""
    echo "Deleting high priority repositories..."
    ./delete_repos.sh delete_high_priority.txt
else
    echo "Skipping high priority deletions."
fi

echo ""
echo "Step 2: Review core projects to keep"
echo "----------------------------------------"
echo "These 20 projects have real commits and are original work:"
echo ""
echo "1. signal-based-recruitment (22 commits)"
echo "2. agentchat (13 commits) - DEPLOYED"
echo "3. coding-tutor-v2 (18 commits)"
echo "4. multi-agent-plugins (18 commits)"
echo "5. Strudel-music-pattern-memory-bank (15 commits)"
echo "6. coding-tutor (15 commits)"
echo "7. beat-sensei (15 commits)"
echo "8. linkedin-face-crm (11 commits)"
echo "9. github-repo-agent (11 commits)"
echo "10. deepseek-code-server (13 commits)"
echo "11. agent-gym (12 commits)"
echo "12. signalfox (10 commits)"
echo "13. contextual-workspace (10 commits)"
echo "14. agent-highway (10 commits)"
echo "15. cli-manager-mcp (9 commits)"
echo "16. vc-intelligence-mcp (8 commits)"
echo "17. next-100-days (8 commits)"
echo "18. snow-globe-app (14 commits)"
echo "19. complianceos-mvp (26 commits)"
echo "20. moltworker (23 commits)"
echo ""

echo "Step 3: Next actions"
echo "----------------------------------------"
echo ""
echo "After deleting templates/forks:"
echo "1. Review remaining repositories:"
echo "   gh repo list yksanjo --limit 50"
echo ""
echo "2. Begin polishing top projects:"
echo "   cd signal-based-recruitment"
echo "   # Update README, add screenshots, etc."
echo ""
echo "3. Create final 'keep' list of 30 repositories"
echo "4. Delete everything else"
echo ""
echo "Detailed plan in FINAL_CLEANUP_PLAN.md"

echo ""
echo "=========================================="
echo "📋 SUMMARY"
echo "=========================================="
echo ""
echo "Immediate action: Delete 23 templates/forks"
echo "Next week: Select best 30 repositories"
echo "Final goal: Clean, focused GitHub profile"
echo ""
echo "Remember: Quality over quantity!"
echo "30 great repos > 500 mediocre repos"