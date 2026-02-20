# GitHub Cleanup Checklist

## Current Status: 500 repositories
**Target: 30-50 high-quality repositories**

## Phase 1: Immediate Cleanup (Week 1)
**Target: 500 → ~400 repositories**

### ✅ Step 1: Delete Templates & Demos (13 repos)
- [ ] Review `phase1_delete.txt`
- [ ] Run `./delete_repos.sh phase1_delete.txt`
- [ ] Verify deletions completed

### 🔍 Step 2: Review Poor-Description Repos (105 repos)
- [ ] Review `poor_desc_repos.txt`
- [ ] Identify which to delete
- [ ] Create `phase2_delete.txt`
- [ ] Delete selected repositories

### 🎯 Step 3: Initial Review
- [ ] Get current count: `gh repo list yksanjo | wc -l`
- [ ] Aim for ~400 repositories by end of Week 1

## Phase 2: Selective Cleanup (Week 2)
**Target: ~400 → ~100 repositories**

### 🔍 Step 1: Review Agent Repositories (107 repos)
- [ ] List all agent repos: `gh repo list yksanjo | grep -i agent`
- [ ] Select best 10-15 to keep
- [ ] Create delete list for the rest
- [ ] Delete unselected agent repos

### 🔍 Step 2: Review AI Repositories (106 repos)
- [ ] List all AI repos: `gh repo list yksanjo | grep -i -E '(ai|llm|gpt)'`
- [ ] Select best 5-10 to keep
- [ ] Create delete list for the rest
- [ ] Delete unselected AI repos

### 🔍 Step 3: Review Tool/Utility Repos (114 repos)
- [ ] List all tool repos
- [ ] Select best 10-15 to keep
- [ ] Create delete list for the rest
- [ ] Delete unselected tool repos

### 🎯 Step 4: Midpoint Review
- [ ] Get current count
- [ ] Aim for ~100 repositories by end of Week 2
- [ ] Create `keep_candidates.txt` with ~100 repos

## Phase 3: Final Selection (Week 3)
**Target: ~100 → 30-50 repositories**

### ✅ Step 1: Core Projects (20 repos - DEFINITELY KEEP)
- [ ] signal-based-recruitment
- [ ] agentchat
- [ ] coding-tutor-v2
- [ ] multi-agent-plugins
- [ ] Strudel-music-pattern-memory-bank
- [ ] coding-tutor
- [ ] beat-sensei
- [ ] linkedin-face-crm
- [ ] github-repo-agent
- [ ] deepseek-code-server
- [ ] agent-gym
- [ ] signalfox
- [ ] contextual-workspace
- [ ] agent-highway
- [ ] cli-manager-mcp
- [ ] vc-intelligence-mcp
- [ ] next-100-days
- [ ] snow-globe-app
- [ ] complianceos-mvp
- [ ] moltworker

### 🔍 Step 2: Additional Selection (10-30 repos)
- [ ] Review remaining ~80 repositories
- [ ] Select additional 10-30 to keep
- [ ] Criteria: Originality, quality, completeness, usefulness
- [ ] Create final `keep_final.txt` (30-50 repos)

### 🗑️ Step 3: Final Deletions
- [ ] Create `delete_final.txt` (everything not in `keep_final.txt`)
- [ ] Review carefully
- [ ] Delete all repositories in `delete_final.txt`

### 🎯 Step 4: Final Count
- [ ] Verify final count: 30-50 repositories
- [ ] All kept repositories are high-quality original work

## Phase 4: Polish & Document (Week 4)
**Target: Professional GitHub profile**

### 📝 Step 1: README Polish
- [ ] For each kept repository:
  - [ ] Update README.md with clear description
  - [ ] Add installation instructions
  - [ ] Add usage examples
  - [ ] Add screenshots (if applicable)
  - [ ] Add deployment information (if deployed)
  - [ ] Add tech stack
  - [ ] Add license

### 🖼️ Step 2: Visual Polish
- [ ] Add repository topics
- [ ] Add proper descriptions
- [ ] Ensure consistent naming
- [ ] Add badges (build status, version, etc.)

### 🌐 Step 3: GitHub Profile
- [ ] Create `yksanjo` profile repository
- [ ] Write compelling profile README
- [ ] Pin 6 best projects
- [ ] Add links to other profiles

### 🔗 Step 4: External Profiles
- [ ] Update LinkedIn profile
- [ ] Update other social media
- [ ] Create consistent narrative
- [ ] Highlight key projects

## Tools & Files

### Analysis Files:
- `phase1_delete.txt` - 13 templates/demos to delete
- `poor_desc_repos.txt` - 105 repos with poor descriptions
- `phase2_candidates.txt` - Combined list for review

### Scripts:
- `delete_repos.sh` - Delete repositories from a list
- `github_cleanup_master.sh` - Master cleanup script
- `phased_cleanup_plan.sh` - Phased cleanup plan
- `analyze_commit_history.sh` - Analyze commit history

### Documentation:
- `FINAL_CLEANUP_PLAN.md` - Complete cleanup plan
- `README.md` - Project overview
- `PROFILE_README.md` - Profile README template

## Progress Tracking

### Week 1 Progress:
- Start: 500 repositories
- Target: ~400 repositories
- Actual: _____ repositories
- Notes: _____

### Week 2 Progress:
- Start: _____ repositories
- Target: ~100 repositories
- Actual: _____ repositories
- Notes: _____

### Week 3 Progress:
- Start: _____ repositories
- Target: 30-50 repositories
- Actual: _____ repositories
- Notes: _____

### Week 4 Progress:
- Repositories polished: _____ / _____
- Profile created: [ ] Yes [ ] No
- External profiles updated: [ ] Yes [ ] No

## Success Criteria

- [ ] 30-50 high-quality repositories
- [ ] All repositories properly documented
- [ ] GitHub profile created and polished
- [ ] External profiles updated
- [ ] Clear, honest narrative established
- [ ] Can confidently explain each project

## Notes

- Quality over quantity
- Keep only original work
- Document everything you keep
- Be honest about your experience
- A clean profile is more impressive than a cluttered one

**Last updated:** $(date)