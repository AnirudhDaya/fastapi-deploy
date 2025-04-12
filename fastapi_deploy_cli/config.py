"""
Configuration handling for FastAPI Deploy CLI.
"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    """Configuration manager for FastAPI Deploy CLI."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file, defaults to ~/.fastapi-deploy/config.yml
        """
        if config_path is None:
            self.config_dir = Path.home() / ".fastapi-deploy"
            self.config_path = self.config_dir / "config.yml"
        else:
            self.config_path = Path(config_path)
            self.config_dir = self.config_path.parent
        
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file or create default.
        
        Returns:
            Dict containing configuration
        """
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.config_path.exists():
            # Create default config
            default_config = {
                "templates_dir": None,  # Will use bundled templates if None
                "default_package_manager": "uv",
                "github_api_url": "https://github-secrets.vercel.app/api/github-secrets",
            }
            
            with open(self.config_path, 'w') as f:
                yaml.dump(default_config, f)
            
            return default_config
        
        # Load existing config
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def save(self) -> None:
        """Save configuration to file."""
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
        self.save()
    
    def get_templates_dir(self) -> Path:
        """
        Get templates directory path.
        
        Returns:
            Path to templates directory
        """
        templates_dir = self.get("templates_dir")
        
        if templates_dir is None:
            # Use bundled templates
            return Path(__file__).parent / "templates"
        
        return Path(templates_dir)