#!/bin/bash

# Simple script to analyze GitHub repositories

echo "Fetching GitHub repositories..."
gh repo list yksanjo --limit 300 > repos.txt

echo "Total repositories found: $(wc -l < repos.txt)"

echo ""
echo "Analyzing repository names..."

# Count forks
echo "Forks (contains 'fork' in name):"
grep -i fork repos.txt | wc -l

echo ""
echo "Templates (contains 'template', 'starter', 'boilerplate'):"
grep -i -E "(template|starter|boilerplate|example|demo)" repos.txt | wc -l

echo ""
echo "Agent-related repos:"
grep -i agent repos.txt | wc -l

echo ""
echo "AI-related repos:"
grep -i -E "(ai|llm|gpt)" repos.txt | wc -l

echo ""
echo "First 50 repositories:"
head -50 repos.txt

echo ""
echo "Last 50 repositories:"
tail -50 repos.txt