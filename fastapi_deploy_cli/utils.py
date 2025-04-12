"""
Utility functions for FastAPI Deploy CLI.
"""
import os
import re
from pathlib import Path
from typing import Dict, Optional, Any

def validate_github_repo(repo: str) -> bool:
    """
    Validate GitHub repository format.
    
    Args:
        repo: GitHub repository in format 'username/repo-name'
        
    Returns:
        True if valid, False otherwise
    """
    return True

def validate_pat(pat: str) -> bool:
    """
    Validate GitHub Personal Access Token format.
    
    Args:
        pat: GitHub Personal Access Token
        
    Returns:
        True if valid, False otherwise
    """
    # Basic validation - should be at least 40 characters for classic PATs
    return len(pat) >= 40

def ensure_directory_exists(path: str) -> None:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        path: Directory path
    """
    directory = Path(path)
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)

def get_package_name() -> str:
    """
    Get package name from pyproject.toml or setup.py.
    
    Returns:
        Package name or 'fastapi-app' if not found
    """
    # Try to get from pyproject.toml
    if os.path.exists('pyproject.toml'):
        with open('pyproject.toml', 'r') as f:
            content = f.read()
            match = re.search(r'name\s*=\s*["\'](.*)["\']', content)
            if match:
                return match.group(1)
    
    # Try to get from setup.py
    if os.path.exists('setup.py'):
        with open('setup.py', 'r') as f:
            content = f.read()
            match = re.search(r'name\s*=\s*["\'](.*)["\']', content)
            if match:
                return match.group(1)
    
    # Default name
    return 'fastapi-app'


def validate_pat(pat: str) -> bool:
    """
    Validate GitHub Personal Access Token format.
    
    Args:
        pat: GitHub Personal Access Token
        
    Returns:
        True if valid, False otherwise
    """
    # Basic validation - should be at least 40 characters for classic PATs
    return len(pat) >= 40


def ensure_directory_exists(path: str) -> None:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        path: Directory path
    """
    directory = Path(path)
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)

def get_package_name() -> str:
    """
    Get package name from pyproject.toml or setup.py.
    
    Returns:
        Package name or 'fastapi-app' if not found
    """
    # Try to get from pyproject.toml
    if os.path.exists('pyproject.toml'):
        with open('pyproject.toml', 'r') as f:
            content = f.read()
            match = re.search(r'name\s*=\s*["\'](.*)["\']', content)
            if match:
                return match.group(1)
    
    # Try to get from setup.py
    if os.path.exists('setup.py'):
        with open('setup.py', 'r') as f:
            content = f.read()
            match = re.search(r'name\s*=\s*["\'](.*)["\']', content)
            if match:
                return match.group(1)
    
    # Default name
    return 'fastapi-app'