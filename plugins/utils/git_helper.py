"""
Git helper plugin.
"""

import os
import subprocess
from typing import Any, Dict, List, Optional
from pydantic import Field

from plugins.base import BasePlugin, BasePluginConfig


class GitHelperConfig(BasePluginConfig):
    """Configuration for git helper."""
    repo_path: str = Field(default=".", description="Repository path")
    author_name: str = Field(default="", description="Git author name")
    author_email: str = Field(default="", description="Git author email")


class GitHelper(BasePlugin):
    """
    Git operations helper.
    """
    
    name = "git_helper"
    version = "1.0.0"
    author = "Multi-Agent Plugins"
    description = "Git operations helper"
    tags = ["utility", "git", "version-control"]
    config_class = GitHelperConfig
    
    def _run_git(self, args: List[str], cwd: Optional[str] = None) -> Dict[str, Any]:
        """Run a git command."""
        repo_path = cwd or self.config.repo_path
        
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return {
                "success": True,
                "output": result.stdout,
                "error": result.stderr
            }
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "output": e.stdout,
                "error": e.stderr
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": "Git not found. Is git installed?"
            }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute git operations.
        
        Args:
            operation: Operation to perform (status, commit, push, pull, branch, log, etc.)
            **kwargs: Operation-specific arguments
            
        Returns:
            Dictionary with operation result
        """
        operation = kwargs.get("operation", "status")
        
        if operation == "status":
            return self._status(kwargs)
        elif operation == "commit":
            return self._commit(kwargs)
        elif operation == "push":
            return self._push(kwargs)
        elif operation == "pull":
            return self._pull(kwargs)
        elif operation == "branch":
            return self._branch(kwargs)
        elif operation == "log":
            return self._log(kwargs)
        elif operation == "diff":
            return self._diff(kwargs)
        elif operation == "add":
            return self._add(kwargs)
        elif operation == "init":
            return self._init(kwargs)
        elif operation == "clone":
            return self._clone(kwargs)
        else:
            return {"error": f"Unknown operation: {operation}"}
    
    def _status(self, kwargs: Dict) -> Dict[str, Any]:
        """Get git status."""
        return self._run_git(["status", "--porcelain"])
    
    def _commit(self, kwargs: Dict) -> Dict[str, Any]:
        """Commit changes."""
        message = kwargs.get("message")
        if not message:
            return {"error": "Commit message is required"}
        
        # Stage all changes
        self._run_git(["add", "-A"])
        
        # Commit
        result = self._run_git(["commit", "-m", message])
        
        if result["success"]:
            # Get commit hash
            hash_result = self._run_git(["rev-parse", "HEAD"])
            result["commit_hash"] = hash_result.get("output", "").strip()[:7]
        
        return result
    
    def _push(self, kwargs: Dict) -> Dict[str, Any]:
        """Push to remote."""
        remote = kwargs.get("remote", "origin")
        branch = kwargs.get("branch", "")
        
        args = ["push"]
        if remote:
            args.append(remote)
        if branch:
            args.append(branch)
        
        return self._run_git(args)
    
    def _pull(self, kwargs: Dict) -> Dict[str, Any]:
        """Pull from remote."""
        remote = kwargs.get("remote", "origin")
        branch = kwargs.get("branch", "")
        
        args = ["pull"]
        if remote:
            args.append(remote)
        if branch:
            args.append(branch)
        
        return self._run_git(args)
    
    def _branch(self, kwargs: Dict) -> Dict[str, Any]:
        """Branch operations."""
        action = kwargs.get("action", "list")
        
        if action == "list":
            return self._run_git(["branch", "-a"])
        elif action == "create":
            name = kwargs.get("name")
            if not name:
                return {"error": "Branch name is required"}
            return self._run_git(["checkout", "-b", name])
        elif action == "delete":
            name = kwargs.get("name")
            if not name:
                return {"error": "Branch name is required"}
            return self._run_git(["branch", "-d", name])
        else:
            return {"error": f"Unknown branch action: {action}"}
    
    def _log(self, kwargs: Dict) -> Dict[str, Any]:
        """Get git log."""
        limit = kwargs.get("limit", 10)
        result = self._run_git([
            "log",
            f"-n{limit}",
            "--pretty=format:%h|%an|%ae|%ad|%s",
            "--date=short"
        ])
        
        if result["success"] and result.get("output"):
            commits = []
            for line in result["output"].strip().split("\n"):
                if line:
                    parts = line.split("|")
                    if len(parts) >= 5:
                        commits.append({
                            "hash": parts[0],
                            "author": parts[1],
                            "email": parts[2],
                            "date": parts[3],
                            "message": "|".join(parts[4:])
                        })
            result["commits"] = commits
        
        return result
    
    def _diff(self, kwargs: Dict) -> Dict[str, Any]:
        """Get git diff."""
        target = kwargs.get("target", "HEAD")
        return self._run_git(["diff", target])
    
    def _add(self, kwargs: Dict) -> Dict[str, Any]:
        """Stage files."""
        files = kwargs.get("files", [])
        
        if not files:
            return self._run_git(["add", "-A"])
        
        return self._run_git(["add"] + files)
    
    def _init(self, kwargs: Dict) -> Dict[str, Any]:
        """Initialize repository."""
        path = kwargs.get("path", ".")
        return self._run_git(["init"], cwd=path)
    
    def _clone(self, kwargs: Dict) -> Dict[str, Any]:
        """Clone repository."""
        url = kwargs.get("url")
        path = kwargs.get("path", ".")
        
        if not url:
            return {"error": "Repository URL is required"}
        
        return self._run_git(["clone", url, path])
    
    def status(self) -> Dict[str, Any]:
        """Get git status."""
        return self.execute(operation="status")
    
    def commit(self, message: str) -> Dict[str, Any]:
        """Commit changes."""
        return self.execute(operation="commit", message=message)
    
    def push(self, remote: str = "origin", branch: str = "") -> Dict[str, Any]:
        """Push to remote."""
        return self.execute(operation="push", remote=remote, branch=branch)
    
    def pull(self, remote: str = "origin", branch: str = "") -> Dict[str, Any]:
        """Pull from remote."""
        return self.execute(operation="pull", remote=remote, branch=branch)
