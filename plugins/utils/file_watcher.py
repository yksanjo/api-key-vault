"""
File watcher plugin.
"""

import os
import time
from typing import Any, Dict, List, Optional, Callable
from pydantic import Field

from plugins.base import BasePlugin, BasePluginConfig


class FileWatcherConfig(BasePluginConfig):
    """Configuration for file watcher."""
    poll_interval: int = Field(
        default=1,
        description="Polling interval in seconds"
    )
    watch_directories: bool = Field(
        default=False,
        description="Watch directories recursively"
    )


class FileWatcher(BasePlugin):
    """
    Watch files for changes.
    """
    
    name = "file_watcher"
    version = "1.0.0"
    author = "Multi-Agent Plugins"
    description = "Watch files for changes"
    tags = ["utility", "file-watcher", "filesystem"]
    config_class = FileWatcherConfig
    
    def __init__(self, config: Optional[FileWatcherConfig] = None):
        super().__init__(config)
        self._watched_files: Dict[str, float] = {}
        self._callbacks: List[Callable] = []
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Watch files for changes.
        
        Args:
            operation: Operation to perform (watch, stop, list)
            path: File or directory path to watch
            callback: Callback function to call on changes
            **kwargs: Additional options
            
        Returns:
            Dictionary with operation result
        """
        operation = kwargs.get("operation", "watch")
        
        if operation == "watch":
            return self._watch(kwargs)
        elif operation == "stop":
            return self._stop_watching(kwargs)
        elif operation == "list":
            return self._list_watched(kwargs)
        elif operation == "check":
            return self._check_changes(kwargs)
        else:
            return {"error": f"Unknown operation: {operation}"}
    
    def _watch(self, kwargs: Dict) -> Dict[str, Any]:
        """Start watching a file or directory."""
        path = kwargs.get("path")
        
        if not path:
            return {"error": "Path is required"}
        
        if not os.path.exists(path):
            return {"error": f"Path does not exist: {path}"}
        
        # Add callback if provided
        callback = kwargs.get("callback")
        if callback:
            self._callbacks.append(callback)
        
        if os.path.isfile(path):
            self._watched_files[path] = os.path.getmtime(path)
        elif os.path.isdir(path):
            # Watch all files in directory
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        self._watched_files[file_path] = os.path.getmtime(file_path)
                    except OSError:
                        pass
        
        return {
            "success": True,
            "path": path,
            "watching": len(self._watched_files)
        }
    
    def _stop_watching(self, kwargs: Dict) -> Dict[str, Any]:
        """Stop watching files."""
        path = kwargs.get("path")
        
        if path:
            # Remove specific path
            if path in self._watched_files:
                del self._watched_files[path]
        else:
            # Clear all
            self._watched_files.clear()
        
        return {
            "success": True,
            "watching": len(self._watched_files)
        }
    
    def _list_watched(self, kwargs: Dict) -> Dict[str, Any]:
        """List watched files."""
        return {
            "files": list(self._watched_files.keys()),
            "count": len(self._watched_files)
        }
    
    def _check_changes(self, kwargs: Dict) -> Dict[str, Any]:
        """Check for file changes."""
        changes = []
        
        for file_path, last_mtime in list(self._watched_files.items()):
            try:
                current_mtime = os.path.getmtime(file_path)
                if current_mtime != last_mtime:
                    changes.append({
                        "path": file_path,
                        "type": "modified",
                        "old_mtime": last_mtime,
                        "new_mtime": current_mtime
                    })
                    self._watched_files[file_path] = current_mtime
            except OSError:
                # File was deleted
                changes.append({
                    "path": file_path,
                    "type": "deleted"
                })
                del self._watched_files[file_path]
        
        # Call callbacks
        for callback in self._callbacks:
            try:
                callback(changes)
            except Exception:
                pass
        
        return {
            "changes": changes,
            "count": len(changes)
        }
    
    def watch(self, path: str, callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Watch a file or directory."""
        return self.execute(operation="watch", path=path, callback=callback)
    
    def check(self) -> Dict[str, Any]:
        """Check for changes."""
        return self.execute(operation="check")
    
    def unwatch(self, path: Optional[str] = None) -> Dict[str, Any]:
        """Stop watching."""
        return self.execute(operation="stop", path=path)
