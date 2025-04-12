"""
File operations for FastAPI Deploy CLI.
"""
import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi_deploy_cli.config import Config

class FileOps:
    """Handles file operations for deployment setup."""
    
    def __init__(self, package_manager: str = "uv", env_path: str = ".env"):
        """
        Initialize file operations.
        
        Args:
            package_manager: Package manager to use ('pip' or 'uv')
            env_path: Path to .env file (not parsed, just copied)
        """
        self.package_manager = package_manager
        self.env_path = env_path
        self.config = Config()
        self.templates_dir = self.config.get_templates_dir()
        
        # Ensure the .github/workflows directory exists
        self.github_dir = Path(".github")
        self.workflows_dir = self.github_dir / "workflows"
        
        if not self.github_dir.exists():
            self.github_dir.mkdir(exist_ok=True)
        
        if not self.workflows_dir.exists():
            self.workflows_dir.mkdir(exist_ok=True)
    
    def _copy_template(self, template_name: str, target_path: Path) -> bool:
        """
        Copy template file to target path without modification.
        
        Args:
            template_name: Template file name
            target_path: Target file path
            
        Returns:
            True if successful, False otherwise
        """
        template_path = self._get_template_path(template_name)
        
        try:
            shutil.copy(template_path, target_path)
            return True
        except Exception as e:
            print(f"Error copying template {template_name}: {e}")
            return False
    
    def _get_template_path(self, file_name: str) -> Path:
        """
        Get template file path.
        
        Args:
            file_name: Template file name
            
        Returns:
            Path to template file
        """
        return self.templates_dir / self.package_manager / file_name
    
    def setup_dockerfile(self) -> bool:
        """
        Set up Dockerfile.
        
        Returns:
            True if successful, False otherwise
        """
        return self._copy_template("Dockerfile", Path("Dockerfile"))
    
    def setup_docker_compose(self) -> bool:
        """
        Set up docker-compose.yml.
        
        Returns:
            True if successful, False otherwise
        """
        return self._copy_template("docker-compose.yml", Path("docker-compose.yml"))
    
    def setup_github_workflow(self) -> bool:
        """
        Set up GitHub Actions workflow file.
        
        Returns:
            True if successful, False otherwise
        """
        workflow_path = self.workflows_dir / "deploy.yml"
        return self._copy_template("deploy.yml", workflow_path)