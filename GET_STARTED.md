# Get Started with GitHub Cleanup

## Quick Start

### 1. Review the Plan
```bash
# View the master cleanup plan
./github_cleanup_master.sh

# Or read the detailed plan
cat FINAL_CLEANUP_PLAN.md
```

### 2. Start Phase 1 (Immediate Cleanup)
```bash
# See what will be deleted
cat phase1_delete.txt

# Delete 13 templates/demos
./delete_repos.sh phase1_delete.txt
```

### 3. Track Your Progress
```bash
# Check current repository count
gh repo list yksanjo | wc -l

# Follow the checklist
cat CLEANUP_CHECKLIST.md
```

## The Problem
- **500 repositories** on GitHub
- Many are templates, demos, or low-quality
- Your **real work is buried**
- Hard to see what you've actually built

## The Solution
Reduce from **500 → 30-50** high-quality repositories.

### Keep These 20 Core Projects:
These have **real commits** and are **original work**:

1. **signal-based-recruitment** (22 commits)
2. **agentchat** (13 commits) - DEPLOYED
3. **coding-tutor-v2** (18 commits)
4. **multi-agent-plugins** (18 commits)
5. **Strudel-music-pattern-memory-bank** (15 commits)
6. **coding-tutor** (15 commits)
7. **beat-sensei** (15 commits)
8. **linkedin-face-crm** (11 commits)
9. **github-repo-agent** (11 commits)
10. **deepseek-code-server** (13 commits)
11. **agent-gym** (12 commits)
12. **signalfox** (10 commits)
13. **contextual-workspace** (10 commits)
14. **agent-highway** (10 commits)
15. **cli-manager-mcp** (9 commits)
16. **vc-intelligence-mcp** (8 commits)
17. **next-100-days** (8 commits)
18. **snow-globe-app** (14 commits)
19. **complianceos-mvp** (26 commits)
20. **moltworker** (23 commits)

## 4-Week Plan

### Week 1: Immediate Cleanup
- Delete 13 templates/demos
- Review 105 poor-description repos
- Target: 500 → ~400 repos

### Week 2: Selective Cleanup
- Review agent repos (keep best 10-15)
- Review AI repos (keep best 5-10)
- Target: ~400 → ~100 repos

### Week 3: Final Selection
- Keep best 30-50 repos total
- Delete everything else
- Target: ~100 → 30-50 repos

### Week 4: Polish & Document
- Update READMEs for all kept repos
- Add screenshots and documentation
- Create GitHub profile
- Update LinkedIn

## Key Principles

1. **Quality over quantity** - 30 great repos > 500 mediocre ones
2. **Keep only original work** - Delete all forks and templates
3. **Document everything** - Each kept repo needs a proper README
4. **Be honest** - Don't claim forks as your work
5. **Show deployed projects** - Highlight agentchat (deployed on Vercel)

## Tools Available

### Analysis Tools:
```bash
# Analyze commit history
./analyze_commit_history.sh

# Identify inactive repos
./identify_inactive_repos.sh

# Categorize repositories
python3 categorize_repos.py
```

### Cleanup Tools:
```bash
# Delete repositories from a list
./delete_repos.sh <list_file>

# Generate delete lists
./create_final_delete_list.sh

# Phased cleanup plan
./phased_cleanup_plan.sh
```

### Guidance:
```bash
# Master cleanup script (interactive)
./github_cleanup_master.sh
```

## Immediate Action

### Today:
```bash
# 1. Delete the obvious junk
./delete_repos.sh phase1_delete.txt

# 2. Check progress
gh repo list yksanjo | wc -l

# 3. Start polishing your best project
cd signal-based-recruitment
# Update README.md, add screenshots, etc.
```

### This Week:
1. Delete Phase 1 templates (13 repos)
2. Review poor-description repos (105 repos)
3. Aim for ~400 repositories by week's end

## Success Metrics

- **Before:** 500 repos (cluttered, hard to navigate)
- **Week 1:** ~400 repos (removed templates)
- **Week 2:** ~100 repos (selected best work)
- **Week 3:** 30-50 repos (final selection)
- **Week 4:** Polished, professional GitHub profile

## Need Help?

1. Review `FINAL_CLEANUP_PLAN.md` for detailed plan
2. Use `CLEANUP_CHECKLIST.md` to track progress
3. Run `./github_cleanup_master.sh` for interactive guidance
4. Check `README.md` for overview

## Remember

A **clean, focused GitHub profile** with 30 great projects is more impressive than a **cluttered profile** with 500 mediocre ones.

**Start now:** `./delete_repos.sh phase1_delete.txt`