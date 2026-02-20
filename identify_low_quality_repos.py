#!/usr/bin/env python3
"""
Identify low-quality repositories for deletion.
"""

import subprocess
import json
import re
from datetime import datetime

def get_repo_details(repo_name):
    """Get detailed information about a repository."""
    cmd = f"gh repo view yksanjo/{repo_name} --json name,description,isFork,createdAt,pushedAt,stargazerCount,repositoryTopics"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return json.loads(result.stdout)
    except:
        pass
    return None

def analyze_repo_quality(repo):
    """Analyze repository quality."""
    name = repo['name']
    details = get_repo_details(name)
    
    if not details:
        return {'name': name, 'quality': 'unknown', 'reason': 'could not fetch details'}
    
    # Quality indicators
    quality_score = 0
    reasons = []
    
    # Negative indicators
    if details.get('isFork', False):
        quality_score -= 10
        reasons.append('fork')
    
    # Check if it's a template
    description = details.get('description', '').lower()
    if any(word in description for word in ['template', 'starter', 'boilerplate', 'example', 'demo']):
        quality_score -= 5
        reasons.append('template')
    
    # Check name patterns
    template_patterns = [r'template', r'starter', r'boilerplate', r'example', r'demo', r'sample']
    for pattern in template_patterns:
        if re.search(pattern, name, re.IGNORECASE):
            quality_score -= 5
            reasons.append('name indicates template')
            break
    
    # Check age and activity
    created_at_str = details['createdAt'].replace('Z', '+00:00')
    created_at = datetime.fromisoformat(created_at_str).replace(tzinfo=None)
    
    pushed_at_str = details.get('pushedAt', details['createdAt']).replace('Z', '+00:00')
    pushed_at = datetime.fromisoformat(pushed_at_str).replace(tzinfo=None)
    
    days_since_creation = (datetime.now() - created_at).days
    days_since_push = (datetime.now() - pushed_at).days
    
    if days_since_push > 30:
        quality_score -= 2
        reasons.append('inactive')
    
    # Check if it has stars
    if details.get('stargazerCount', 0) == 0:
        quality_score -= 1
        reasons.append('no stars')
    
    # Check description quality
    if not description or len(description) < 10:
        quality_score -= 3
        reasons.append('poor description')
    
    # Determine quality category
    if quality_score <= -10:
        quality = 'very_low'
    elif quality_score <= -5:
        quality = 'low'
    elif quality_score <= 0:
        quality = 'medium'
    else:
        quality = 'high'
    
    return {
        'name': name,
        'quality': quality,
        'score': quality_score,
        'reasons': reasons,
        'is_fork': details.get('isFork', False),
        'description': details.get('description', ''),
        'stars': details.get('stargazerCount', 0),
        'created_at': details['createdAt'],
        'pushed_at': details.get('pushedAt', details['createdAt']),
    }

def main():
    """Main function to identify low-quality repositories."""
    print("Identifying low-quality repositories...")
    
    # Get all repositories
    cmd = "gh repo list yksanjo --limit 500 --json name"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return
    
    repos = json.loads(result.stdout)
    print(f"Analyzing {len(repos)} repositories...")
    
    # Analyze each repository
    analyzed = []
    for i, repo in enumerate(repos):
        print(f"Analyzing {i+1}/{len(repos)}: {repo['name']}")
        analysis = analyze_repo_quality(repo)
        analyzed.append(analysis)
    
    # Categorize by quality
    categories = {
        'very_low': [],
        'low': [],
        'medium': [],
        'high': [],
        'unknown': []
    }
    
    for analysis in analyzed:
        categories[analysis['quality']].append(analysis)
    
    # Print summary
    print("\n" + "="*60)
    print("REPOSITORY QUALITY ANALYSIS")
    print("="*60)
    
    for quality, repos in categories.items():
        print(f"\n{quality.upper()} ({len(repos)}):")
        for repo in sorted(repos, key=lambda x: x['score'])[:10]:
            print(f"  - {repo['name']} (score: {repo['score']}, reasons: {', '.join(repo['reasons'])})")
        if len(repos) > 10:
            print(f"  ... and {len(repos) - 10} more")
    
    # Generate delete recommendations
    print("\n" + "="*60)
    print("DELETE RECOMMENDATIONS")
    print("="*60)
    
    # Very low quality (definitely delete)
    very_low = [r['name'] for r in categories['very_low']]
    
    # Low quality (probably delete)
    low = [r['name'] for r in categories['low']]
    
    # Write delete lists
    with open('delete_very_low_quality.txt', 'w') as f:
        f.write("# Very low quality repositories (definitely delete)\n")
        for repo in sorted(very_low):
            f.write(f"{repo}\n")
    
    with open('delete_low_quality.txt', 'w') as f:
        f.write("# Low quality repositories (probably delete)\n")
        for repo in sorted(low):
            f.write(f"{repo}\n")
    
    print(f"\nVery low quality: {len(very_low)} repositories")
    print(f"Low quality: {len(low)} repositories")
    print(f"\nTotal recommended deletions: {len(very_low) + len(low)}")
    
    # Save full analysis
    with open('repo_quality_analysis.json', 'w') as f:
        json.dump({
            'total_repos': len(analyzed),
            'categories': {k: len(v) for k, v in categories.items()},
            'repos': analyzed
        }, f, indent=2, default=str)
    
    print("\nAnalysis complete. Files created:")
    print("- delete_very_low_quality.txt")
    print("- delete_low_quality.txt")
    print("- repo_quality_analysis.json")

if __name__ == "__main__":
    main()