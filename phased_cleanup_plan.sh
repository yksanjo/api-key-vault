#!/bin/bash

# Phased cleanup plan for GitHub organization

echo "=========================================="
echo "PHASED GITHUB CLEANUP PLAN"
echo "=========================================="
echo ""
echo "Current: 500 repositories"
echo "Phase 1: Delete obvious junk (50 repos)"
echo "Phase 2: Review and select (100 repos)"
echo "Phase 3: Final selection (50 repos)"
echo "Phase 4: Polish and document (30 repos)"
echo ""

echo "PHASE 1: Delete Obvious Junk"
echo "-----------------------------"
echo ""

# Get obvious templates and demos
echo "1. Templates and demos:"
gh repo list yksanjo --limit 500 | grep -i -E "(template|starter|boilerplate|example|demo|sample)" | cut -f1 | cut -d'/' -f2 > phase1_templates.txt
cat phase1_templates.txt
echo "Count: $(wc -l < phase1_templates.txt)"
echo ""

# Get forks
echo "2. Forks:"
gh repo list yksanjo --limit 500 --json name,isFork | jq -r '.[] | select(.isFork == true) | .name' > phase1_forks.txt
cat phase1_forks.txt
echo "Count: $(wc -l < phase1_forks.txt)"
echo ""

# Combine Phase 1 deletions
cat phase1_templates.txt phase1_forks.txt | sort -u > phase1_delete.txt
PHASE1_COUNT=$(wc -l < phase1_delete.txt)
echo "Total Phase 1 deletions: $PHASE1_COUNT"
echo ""

echo "PHASE 2: Review Categories"
echo "--------------------------"
echo ""

# Count repositories by category
echo "Repository categories:"
echo "- Agent-related: $(gh repo list yksanjo --limit 500 | grep -i agent | wc -l)"
echo "- AI-related: $(gh repo list yksanjo --limit 500 | grep -i -E '(ai|llm|gpt)' | wc -l)"
echo "- Tool/Utility: $(gh repo list yksanjo --limit 500 | grep -i -E '(cli|tool|util|helper|manager)' | wc -l)"
echo "- Project: $(gh repo list yksanjo --limit 500 | grep -i -E '(signal|coding|beat|linkedin|snow|strudel|moltworker|compliance|apihub)' | wc -l)"
echo ""

echo "PHASE 3: Core Projects to KEEP"
echo "-------------------------------"
echo ""

# Core projects (from analysis)
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

echo "20 Core projects (definitely keep):"
for project in "${CORE_PROJECTS[@]}"; do
    echo "- $project"
done
echo ""

echo "PHASE 4: Action Plan"
echo "--------------------"
echo ""

echo "Week 1: Immediate cleanup"
echo "  ./delete_repos.sh phase1_delete.txt"
echo "  Expected: 500 → $((500 - PHASE1_COUNT)) repositories"
echo ""

echo "Week 2: Review agent repositories"
echo "  Keep best 10-15 agent repos"
echo "  Delete the rest"
echo "  Expected: $((500 - PHASE1_COUNT)) → ~100 repositories"
echo ""

echo "Week 3: Final selection"
echo "  Keep best 30-50 repositories total"
echo "  Delete everything else"
echo "  Expected: ~100 → 30-50 repositories"
echo ""

echo "Week 4: Polish and document"
echo "  Update READMEs for all kept repos"
echo "  Add screenshots and documentation"
echo "  Create GitHub profile"
echo ""

echo "Files created:"
echo "- phase1_templates.txt (templates/demos)"
echo "- phase1_forks.txt (forks)"
echo "- phase1_delete.txt (all Phase 1 deletions)"
echo ""

echo "To start Phase 1:"
echo "  ./delete_repos.sh phase1_delete.txt"
echo ""
echo "Review before deleting:"
echo "  cat phase1_delete.txt"
echo ""
echo "Remember:"
echo "1. Quality over quantity"
echo "2. Keep only original work"
echo "3. Document everything you keep"
echo "4. Be honest about what you built"