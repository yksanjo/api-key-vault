"""
Docker manager plugin.
"""

import subprocess
from typing import Any, Dict, List, Optional
from pydantic import Field

from plugins.base import BasePlugin, BasePluginConfig


class DockerManagerConfig(BasePluginConfig):
    """Configuration for docker manager."""
    default_timeout: int = Field(
        default=60,
        description="Default command timeout in seconds"
    )


class DockerManager(BasePlugin):
    """
    Docker container management.
    """
    
    name = "docker_manager"
    version = "1.0.0"
    author = "Multi-Agent Plugins"
    description = "Manage Docker containers"
    tags = ["utility", "docker", "containers"]
    config_class = DockerManagerConfig
    
    def _run_docker(self, args: List[str]) -> Dict[str, Any]:
        """Run a docker command."""
        try:
            result = subprocess.run(
                ["docker"] + args,
                capture_output=True,
                text=True,
                timeout=self.config.timeout,
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
                "error": "Docker not found. Is Docker installed?"
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Docker command timed out after {self.config.timeout} seconds"
            }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute docker operations.
        
        Args:
            operation: Operation to perform (ps, start, stop, run, rm, logs, etc.)
            **kwargs: Operation-specific arguments
            
        Returns:
            Dictionary with operation result
        """
        operation = kwargs.get("operation", "ps")
        
        if operation == "ps":
            return self._ps(kwargs)
        elif operation == "start":
            return self._start(kwargs)
        elif operation == "stop":
            return self._stop(kwargs)
        elif operation == "run":
            return self._run(kwargs)
        elif operation == "rm":
            return self._rm(kwargs)
        elif operation == "logs":
            return self._logs(kwargs)
        elif operation == "images":
            return self._images(kwargs)
        elif operation == "pull":
            return self._pull(kwargs)
        elif operation == "build":
            return self._build(kwargs)
        elif operation == "exec":
            return self._exec(kwargs)
        else:
            return {"error": f"Unknown operation: {operation}"}
    
    def _ps(self, kwargs: Dict) -> Dict[str, Any]:
        """List containers."""
        all_containers = kwargs.get("all", False)
        
        args = ["ps"]
        if all_containers:
            args.append("-a")
        args.append("--format", "{{.ID}}|{{.Names}}|{{.Status}}|{{.Image}}")
        
        result = self._run_docker(args)
        
        if result["success"] and result.get("output"):
            containers = []
            for line in result["output"].strip().split("\n"):
                if line:
                    parts = line.split("|")
                    if len(parts) >= 4:
                        containers.append({
                            "id": parts[0],
                            "name": parts[1],
                            "status": parts[2],
                            "image": parts[3]
                        })
            result["containers"] = containers
        
        return result
    
    def _start(self, kwargs: Dict) -> Dict[str, Any]:
        """Start a container."""
        container = kwargs.get("container")
        
        if not container:
            return {"error": "Container name or ID is required"}
        
        return self._run_docker(["start", container])
    
    def _stop(self, kwargs: Dict) -> Dict[str, Any]:
        """Stop a container."""
        container = kwargs.get("container")
        
        if not container:
            return {"error": "Container name or ID is required"}
        
        return self._run_docker(["stop", container])
    
    def _run(self, kwargs: Dict) -> Dict[str, Any]:
        """Run a container."""
        image = kwargs.get("image")
        command = kwargs.get("command", "")
        name = kwargs.get("name", "")
        detach = kwargs.get("detach", False)
        ports = kwargs.get("ports", [])
        env = kwargs.get("env", {})
        volumes = kwargs.get("volumes", [])
        
        if not image:
            return {"error": "Image is required"}
        
        args = ["run"]
        
        if detach:
            args.append("-d")
        
        if name:
            args.extend(["--name", name])
        
        for port in ports:
            args.extend(["-p", port])
        
        for key, value in env.items():
            args.extend(["-e", f"{key}={value}"])
        
        for volume in volumes:
            args.extend(["-v", volume])
        
        args.append(image)
        
        if command:
            args.extend(command.split())
        
        return self._run_docker(args)
    
    def _rm(self, kwargs: Dict) -> Dict[str, Any]:
        """Remove a container."""
        container = kwargs.get("container")
        force = kwargs.get("force", False)
        
        if not container:
            return {"error": "Container name or ID is required"}
        
        args = ["rm"]
        if force:
            args.append("-f")
        args.append(container)
        
        return self._run_docker(args)
    
    def _logs(self, kwargs: Dict) -> Dict[str, Any]:
        """Get container logs."""
        container = kwargs.get("container")
        tail = kwargs.get("tail", 100)
        
        if not container:
            return {"error": "Container name or ID is required"}
        
        return self._run_docker(["logs", "--tail", str(tail), container])
    
    def _images(self, kwargs) -> Dict[str, Any]:
        """List images."""
        args = ["images", "--format", "{{.ID}}|{{.Repository}}|{{.Tag}}|{{.Size}}"]
        
        result = self._run_docker(args)
        
        if result["success"] and result.get("output"):
            images = []
            for line in result["output"].strip().split("\n"):
                if line:
                    parts = line.split("|")
                    if len(parts) >= 4:
                        images.append({
                            "id": parts[0],
                            "repository": parts[1],
                            "tag": parts[2],
                            "size": parts[3]
                        })
            result["images"] = images
        
        return result
    
    def _pull(self, kwargs: Dict) -> Dict[str, Any]:
        """Pull an image."""
        image = kwargs.get("image")
        
        if not image:
            return {"error": "Image name is required"}
        
        return self._run_docker(["pull", image])
    
    def _build(self, kwargs: Dict) -> Dict[str, Any]:
        """Build an image."""
        path = kwargs.get("path", ".")
        tag = kwargs.get("tag")
        
        args = ["build"]
        
        if tag:
            args.extend(["-t", tag])
        
        args.append(path)
        
        return self._run_docker(args)
    
    def _exec(self, kwargs: Dict) -> Dict[str, Any]:
        """Execute command in container."""
        container = kwargs.get("container")
        command = kwargs.get("command")
        
        if not container or not command:
            return {"error": "Container and command are required"}
        
        return self._run_docker(["exec", container, "sh", "-c", command])
    
    def list_containers(self, all_containers: bool = False) -> Dict[str, Any]:
        """List containers."""
        return self.execute(operation="ps", all=all_containers)
    
    def start_container(self, container: str) -> Dict[str, Any]:
        """Start a container."""
        return self.execute(operation="start", container=container)
    
    def stop_container(self, container: str) -> Dict[str, Any]:
        """Stop a container."""
        return self.execute(operation="stop", container=container)
    
    def remove_container(self, container: str, force: bool = False) -> Dict[str, Any]:
        """Remove a container."""
        return self.execute(operation="rm", container=container, force=force)
