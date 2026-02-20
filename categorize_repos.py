#!/usr/bin/env python3
"""
Categorize repositories for cleanup.
"""

import subprocess
import json
import re

def get_all_repos():
    """Get all GitHub repositories."""
    print("Fetching all repositories...")
    cmd = "gh repo list yksanjo --limit 500 --json name,description,isFork"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return []
    
    repos = json.loads(result.stdout)
    print(f"Found {len(repos)} repositories")
    return repos

def categorize_repo(repo):
    """Categorize a repository."""
    name = repo['name']
    description = repo.get('description', '').lower()
    is_fork = repo.get('isFork', False)
    
    # Patterns for different categories
    patterns = {
        'template': [
            r'template', r'starter', r'boilerplate', r'example', r'demo', r'sample',
            r'^devcontainer-', r'^pipeline-ai-', r'^scraping-', r'^test-'
        ],
        'agent': [
            r'^agent-', r'-agent$', r'agent-', r'^multi-agent', r'^ai-agent'
        ],
        'ai': [
            r'^ai-', r'-ai$', r'^llm-', r'^gpt-', r'^deepseek-', r'^claude-'
        ],
        'tool': [
            r'^cli-', r'-cli$', r'^tool', r'^util', r'^helper', r'^manager',
            r'^github-', r'^repo-', r'^api-', r'^web-', r'^browser-'
        ],
        'project': [
            r'^signal-', r'^coding-', r'^beat-', r'^linkedin-', r'^snow-',
            r'^strudel-', r'^moltworker', r'^complianceos', r'^apihub',
            r'^ghostly-', r'^mini-build-', r'^death-of-saas'
        ]
    }
    
    # Determine category
    category = 'other'
    
    if is_fork:
        category = 'fork'
    else:
        for cat, cat_patterns in patterns.items():
            for pattern in cat_patterns:
                if re.search(pattern, name, re.IGNORECASE):
                    category = cat
                    break
            if category != 'other':
                break
        
        # Check description
        if category == 'other':
            for cat, cat_patterns in patterns.items():
                for pattern in cat_patterns:
                    if re.search(pattern, description, re.IGNORECASE):
                        category = cat
                        break
                if category != 'other':
                    break
    
    return category

def main():
    """Main categorization function."""
    repos = get_all_repos()
    
    if not repos:
        return
    
    categories = {}
    for repo in repos:
        category = categorize_repo(repo)
        if category not in categories:
            categories[category] = []
        categories[category].append(repo['name'])
    
    # Print summary
    print("\n" + "="*60)
    print("REPOSITORY CATEGORIZATION")
    print("="*60)
    
    total = 0
    for category, repo_list in sorted(categories.items()):
        print(f"\n{category.upper()} ({len(repo_list)}):")
        for repo in sorted(repo_list)[:15]:
            print(f"  - {repo}")
        if len(repo_list) > 15:
            print(f"  ... and {len(repo_list) - 15} more")
        total += len(repo_list)
    
    print(f"\nTotal repositories: {total}")
    
    # Generate delete recommendations
    print("\n" + "="*60)
    print("DELETE RECOMMENDATIONS")
    print("="*60)
    
    # High priority deletions
    high_priority = []
    high_priority.extend(categories.get('template', []))
    high_priority.extend(categories.get('fork', []))
    
    # Medium priority (consider keeping some)
    medium_priority = []
    medium_priority.extend(categories.get('tool', []))
    
    # Low priority (likely keep)
    low_priority = []
    low_priority.extend(categories.get('project', []))
    low_priority.extend(categories.get('agent', []))
    low_priority.extend(categories.get('ai', []))
    
    print(f"\nHigh priority deletions ({len(high_priority)}):")
    print("  Templates and forks")
    
    print(f"\nMedium priority ({len(medium_priority)}):")
    print("  Tools and utilities (review before deleting)")
    
    print(f"\nLow priority ({len(low_priority)}):")
    print("  Projects, agents, AI (likely keep)")
    
    # Write delete lists
    with open('delete_high_priority.txt', 'w') as f:
        f.write("# High priority deletions (templates and forks)\n")
        for repo in sorted(high_priority):
            f.write(f"{repo}\n")
    
    with open('delete_medium_priority.txt', 'w') as f:
        f.write("# Medium priority deletions (tools and utilities)\n")
        for repo in sorted(medium_priority):
            f.write(f"{repo}\n")
    
    with open('keep_recommended.txt', 'w') as f:
        f.write("# Recommended to keep (projects, agents, AI)\n")
        for repo in sorted(low_priority):
            f.write(f"{repo}\n")
    
    print(f"\nFiles created:")
    print(f"- delete_high_priority.txt ({len(high_priority)} repos)")
    print(f"- delete_medium_priority.txt ({len(medium_priority)} repos)")
    print(f"- keep_recommended.txt ({len(low_priority)} repos)")

if __name__ == "__main__":
    main()