# GitHub Organization Cleanup & Organization

This repository contains tools and documentation for organizing the `yksanjo` GitHub organization.

## Current Status

**500 repositories** → **Target: 20-30 high-quality repositories**

### Analysis Results:
- **500 total repositories** on GitHub
- **23 templates/forks** (immediate deletion)
- **65 tools/utilities** (review before deletion)
- **104 projects/agents/AI** (consider keeping)
- **308 other repositories** (manual review needed)

## Cleanup Plan

### Phase 1: Immediate Deletions (Week 1)
- Delete 23 templates and forks
- Target: Reduce from 500 to 200 repositories

### Phase 2: Selective Cleanup (Week 2)
- Review and select best 20-30 repositories
- Delete remaining 400+ repositories
- Target: Reduce from 200 to 30 repositories

### Phase 3: Polish & Document (Week 3)
- Polish READMEs for all kept repositories
- Add screenshots and deployment information
- Ensure proper documentation

### Phase 4: Profile Creation (Week 4)
- Create GitHub profile repository
- Pin 6 best projects
- Update LinkedIn and establish narrative

## Core Projects to Keep (Based on Commit Analysis)

These 20 projects have **real commits** and are **original work**:

1. **signal-based-recruitment** (22 commits) - Recruitment platform
2. **agentchat** (13 commits) - Real-time agent chat (DEPLOYED)
3. **coding-tutor-v2** (18 commits) - Educational platform
4. **multi-agent-plugins** (18 commits) - Agent plugin system
5. **Strudel-music-pattern-memory-bank** (15 commits) - Music pattern library
6. **coding-tutor** (15 commits) - Original coding tutor
7. **beat-sensei** (15 commits) - Music education with AI
8. **linkedin-face-crm** (11 commits) - Face recognition CRM
9. **github-repo-agent** (11 commits) - GitHub automation
10. **deepseek-code-server** (13 commits) - Code server
11. **agent-gym** (12 commits) - Agent training environment
12. **signalfox** (10 commits) - Signal-based tools
13. **contextual-workspace** (10 commits) - Context-aware workspace
14. **agent-highway** (10 commits) - Agent infrastructure
15. **cli-manager-mcp** (9 commits) - CLI management
16. **vc-intelligence-mcp** (8 commits) - VC intelligence
17. **next-100-days** (8 commits) - Progress tracking
18. **snow-globe-app** (14 commits) - Interactive app
19. **complianceos-mvp** (26 commits) - Compliance management
20. **moltworker** (23 commits) - Cloudflare agent runtime

**Note:** `ddsp-piano` has 44 commits but is a FORK - consider deleting.

## Tools

### `delete_repos.sh`
Script to delete GitHub repositories from a list.

```bash
# Delete high priority templates and forks
./delete_repos.sh delete_high_priority.txt

# Review medium priority deletions
cat delete_medium_priority.txt
```

### Analysis Scripts
- `analyze_commit_history.sh` - Analyze commit history of repositories
- `categorize_repos.py` - Categorize repositories for cleanup
- `generate_delete_lists.sh` - Generate delete lists

### Repository Lists
- `delete_high_priority.txt` - 23 templates/forks (immediate deletion)
- `delete_medium_priority.txt` - 65 tools/utilities (review)
- `keep_recommended.txt` - 104 projects/agents/AI (consider keeping)

## Documentation

- `FINAL_CLEANUP_PLAN.md` - Complete cleanup plan based on analysis
- `FINAL_ACTION_PLAN.md` - Original cleanup plan
- `PROFILE_README.md` - GitHub profile README template
- `PROJECT_INDEX.md` - Index of all active projects

## Immediate Next Steps

1. **Delete templates and forks:**
   ```bash
   ./delete_repos.sh delete_high_priority.txt
   ```

2. **Review remaining repositories:**
   ```bash
   gh repo list yksanjo --limit 50
   ```

3. **Begin polishing top projects:**
   ```bash
   cd signal-based-recruitment
   # Update README, add screenshots, etc.
   ```

## License

MIT
