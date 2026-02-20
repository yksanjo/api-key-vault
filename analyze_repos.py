#!/usr/bin/env python3
"""
Analyze GitHub repositories and categorize them for cleanup.
"""

import subprocess
import json
import os
from datetime import datetime, timedelta
import re

def get_github_repos():
    """Get all GitHub repositories for the user."""
    print("Fetching GitHub repositories...")
    
    # Get all repos
    cmd = "gh repo list yksanjo --limit 500 --json name,description,isPrivate,isFork,createdAt,updatedAt,pushedAt,stargazerCount,repositoryTopics"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error fetching repos: {result.stderr}")
        return []
    
    repos = json.loads(result.stdout)
    print(f"Found {len(repos)} repositories")
    return repos

def analyze_repo(repo):
    """Analyze a single repository."""
    name = repo['name']
    
    # Check if it's a fork
    is_fork = repo.get('isFork', False)
    
    # Check age
    created_at = datetime.fromisoformat(repo['createdAt'].replace('Z', '+00:00'))
    days_old = (datetime.now() - created_at).days
    
    # Check activity
    pushed_at = datetime.fromisoformat(repo['pushedAt'].replace('Z', '+00:00')) if repo.get('pushedAt') else created_at
    days_inactive = (datetime.now() - pushed_at).days
    
    # Check if it's a template (based on name patterns)
    is_template = False
    template_patterns = [
        r'^template-',
        r'-template$',
        r'^starter-',
        r'-starter$',
        r'^boilerplate-',
        r'-boilerplate$',
        r'^example-',
        r'-example$',
        r'^demo-',
        r'-demo$',
    ]
    
    for pattern in template_patterns:
        if re.search(pattern, name, re.IGNORECASE):
            is_template = True
            break
    
    # Check description for template indicators
    description = repo.get('description', '').lower()
    template_keywords = ['template', 'starter', 'boilerplate', 'example', 'demo', 'sample']
    if any(keyword in description for keyword in template_keywords):
        is_template = True
    
    # Check topics
    topics = repo.get('repositoryTopics', [])
    topic_names = [t['topic']['name'].lower() for t in topics]
    if any(keyword in topic_names for keyword in template_keywords):
        is_template = True
    
    # Determine category
    category = "unknown"
    
    if is_fork:
        category = "fork"
    elif is_template:
        category = "template"
    elif days_inactive > 180:  # 6 months inactive
        category = "inactive"
    elif repo.get('isPrivate', False):
        category = "private"
    elif days_old < 30:  # New repository
        category = "new"
    else:
        category = "active"
    
    return {
        'name': name,
        'category': category,
        'is_fork': is_fork,
        'is_template': is_template,
        'days_old': days_old,
        'days_inactive': days_inactive,
        'private': repo.get('isPrivate', False),
        'stars': repo.get('stargazerCount', 0),
        'description': repo.get('description', ''),
        'created_at': repo['createdAt'],
        'pushed_at': repo.get('pushedAt', repo['createdAt']),
    }

def main():
    """Main analysis function."""
    repos = get_github_repos()
    
    if not repos:
        print("No repositories found")
        return
    
    analyzed = []
    categories = {}
    
    for repo in repos:
        analysis = analyze_repo(repo)
        analyzed.append(analysis)
        
        category = analysis['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(analysis['name'])
    
    # Print summary
    print("\n" + "="*60)
    print("REPOSITORY ANALYSIS SUMMARY")
    print("="*60)
    
    for category, repos in sorted(categories.items()):
        print(f"\n{category.upper()} ({len(repos)} repos):")
        for repo in sorted(repos)[:10]:  # Show first 10
            print(f"  - {repo}")
        if len(repos) > 10:
            print(f"  ... and {len(repos) - 10} more")
    
    # Generate delete lists
    print("\n" + "="*60)
    print("GENERATING DELETE LISTS")
    print("="*60)
    
    # High confidence deletions (forks and templates)
    high_confidence = []
    for analysis in analyzed:
        if analysis['category'] in ['fork', 'template']:
            high_confidence.append(analysis['name'])
    
    # GitHub only deletions (repos not in local)
    github_only = []
    # We'll need to check local directories for this
    
    # Write delete lists
    if high_confidence:
        with open('delete_high_confidence_new.txt', 'w') as f:
            for repo in sorted(high_confidence):
                f.write(f"{repo}\n")
        print(f"Created delete_high_confidence_new.txt with {len(high_confidence)} repos")
    
    # Write analysis report
    with open('repo_analysis_report.json', 'w') as f:
        json.dump({
            'total_repos': len(analyzed),
            'categories': categories,
            'repos': analyzed
        }, f, indent=2, default=str)
    
    print(f"\nAnalysis complete. Total repos: {len(analyzed)}")
    print(f"High confidence deletions: {len(high_confidence)}")
    
    # Recommendations
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    
    keep_count = len(analyzed) - len(high_confidence)
    print(f"1. Delete {len(high_confidence)} forks and templates")
    print(f"2. Keep {keep_count} active/original repositories")
    print(f"3. Review inactive repos ({len(categories.get('inactive', []))})")
    print(f"4. Consider making private repos public ({len(categories.get('private', []))})")

if __name__ == "__main__":
    main()