# FINAL CLEANUP PLAN - GitHub Organization

Based on analysis of 500 repositories in `yksanjo` GitHub organization.

## Current State
- **500 total repositories**
- **23 templates/forks** (high priority deletions)
- **65 tools/utilities** (medium priority - review)
- **104 projects/agents/AI** (low priority - likely keep)
- **308 other repositories** (need manual review)

## Goal: Reduce to 20-30 High-Quality Repositories

### Phase 1: Immediate Deletions (23 repos)

Delete all templates and forks:

```bash
./delete_repos.sh delete_high_priority.txt
```

**High Priority Deletions:**
- All template repositories (devcontainer-templates-*, pipeline-ai-*, etc.)
- All demo/starter repositories
- Any obvious forks

### Phase 2: Keep These 20 Core Projects

Based on commit history analysis, these are your **original projects with real commits**:

1. **signal-based-recruitment** (22 commits) - ✅ KEEP
2. **agentchat** (13 commits) - ✅ KEEP (DEPLOYED)
3. **coding-tutor-v2** (18 commits) - ✅ KEEP
4. **multi-agent-plugins** (18 commits) - ✅ KEEP
5. **Strudel-music-pattern-memory-bank** (15 commits) - ✅ KEEP
6. **coding-tutor** (15 commits) - ✅ KEEP
7. **beat-sensei** (15 commits) - ✅ KEEP
8. **linkedin-face-crm** (11 commits) - ✅ KEEP
9. **github-repo-agent** (11 commits) - ✅ KEEP
10. **deepseek-code-server** (13 commits) - ✅ KEEP
11. **agent-gym** (12 commits) - ✅ KEEP
12. **signalfox** (10 commits) - ✅ KEEP
13. **contextual-workspace** (10 commits) - ✅ KEEP
14. **agent-highway** (10 commits) - ✅ KEEP
15. **cli-manager-mcp** (9 commits) - ✅ KEEP
16. **vc-intelligence-mcp** (8 commits) - ✅ KEEP
17. **next-100-days** (8 commits) - ✅ KEEP
18. **snow-globe-app** (14 commits) - ✅ KEEP
19. **complianceos-mvp** (26 commits) - ✅ KEEP
20. **moltworker** (23 commits) - ✅ KEEP

**Note:** `ddsp-piano` has 44 commits but is a FORK - consider deleting or keeping as reference.

### Phase 3: Review These Additional Projects (10-20 more)

These have fewer commits but might be worth keeping:

1. **agent-sandbox** (1 commit) - New, promising
2. **ghostly-memory-bank** (3 commits) - New, promising
3. **api-key-vault** (1 commit) - New
4. **apihub** (3 commits) - New
5. **ghostly-core** (check commits)
6. **ghostly-cli** (check commits)
7. **mini-build-web** (check commits)
8. **mini-build-cli** (check commits)
9. **mini-build-game** (check commits)
10. **mini-build-your-own-x** (check commits)

### Phase 4: Delete Everything Else (400+ repos)

After keeping 20-40 repositories, delete the remaining 460+ repositories.

## Action Plan

### Week 1: Immediate Cleanup
1. Delete all templates and forks (23 repos)
2. Review and delete obvious low-quality repositories
3. Target: Reduce from 500 to 200 repos

### Week 2: Selective Cleanup
1. Review agent-related repositories (78 repos) - keep only the best 10-15
2. Review AI-related repositories (17 repos) - keep only the best 5-10
3. Review tool repositories (65 repos) - keep only the best 10-15
4. Target: Reduce from 200 to 50 repos

### Week 3: Final Polish
1. Polish READMEs for top 20 repositories
2. Add screenshots and documentation
3. Ensure all kept repositories are properly documented
4. Target: 30 high-quality repositories

### Week 4: Profile Creation
1. Create GitHub profile repository
2. Pin 6 best projects
3. Update LinkedIn and other profiles
4. Establish clear narrative

## Tools Available

1. **`delete_repos.sh`** - Delete repositories from a list
2. **`delete_high_priority.txt`** - 23 templates/forks to delete
3. **`delete_medium_priority.txt`** - 65 tools/utilities to review
4. **`keep_recommended.txt`** - 104 projects/agents/AI to consider keeping

## Next Steps

### Immediate Action (Today):
```bash
# Delete all templates and forks
./delete_repos.sh delete_high_priority.txt

# Review what's left
gh repo list yksanjo --limit 50
```

### This Week:
1. Review agent repositories and select the best 10-15
2. Review AI repositories and select the best 5-10
3. Create a final "keep" list of 30 repositories
4. Delete everything else

## Success Metrics

- **Current:** 500 repositories (cluttered, hard to navigate)
- **Week 1:** 200 repositories (removed templates/forks)
- **Week 2:** 50 repositories (selected best work)
- **Week 3:** 30 repositories (polished, documented)
- **Final:** Clean, focused GitHub profile with only your best work

## Important Notes

1. **Quality over quantity** - 30 great repositories are better than 500 mediocre ones
2. **Original work only** - Delete all forks and templates
3. **Document everything** - Each kept repository should have a proper README
4. **Show deployed projects** - Highlight agentchat (deployed on Vercel)
5. **Be honest** - Don't claim forks as your work

## Start Now

```bash
# Step 1: Delete the obvious junk
./delete_repos.sh delete_high_priority.txt

# Step 2: Review what's left
echo "Repositories remaining:"
gh repo list yksanjo | wc -l

# Step 3: Begin polishing your top 5 projects
cd signal-based-recruitment
# Add screenshots, update README, etc.
```

**Remember:** A clean, focused GitHub profile is more impressive than a cluttered one with hundreds of repositories.