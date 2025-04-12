"""
Environment file handler for FastAPI Deploy CLI.
"""
import os
from pathlib import Path
from typing import List

class EnvHandler:
    """Handles .env file operations."""
    
    def __init__(self, env_path: str = ".env"):
        """
        Initialize environment handler.
        
        Args:
            env_path: Path to .env file
        """
        self.env_path = Path(env_path)
    
    def file_exists(self) -> bool:
        """Check if the .env file exists."""
        return self.env_path.exists()
        
    def get_file_path(self) -> str:
        """Get the full path to the .env file."""
        return str(self.env_path.absolute())
        
    def check_required_vars(self, required_vars: List[str]) -> List[str]:
        """
        Check if env file contains required variables.
        Only checks existence, not actual values.
        
        Args:
            required_vars: List of required variable names
            
        Returns:
            List of missing variable names
        """
        if not self.file_exists():
            return required_vars
            
        # Read file and check for variables
        with open(self.env_path, 'r') as f:
            content = f.read()
            
        missing = []
        for var in required_vars:
            # Simple check if variable name appears in file
            if f"{var}=" not in content:
                missing.append(var)
                
        return missing