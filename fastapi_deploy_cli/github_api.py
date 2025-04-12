"""
GitHub API handler for FastAPI Deploy CLI.
"""
import requests
from pathlib import Path
from typing import Dict, Any

from fastapi_deploy_cli.config import Config

class GithubSecrets:
    """Handler for GitHub Secrets API interactions."""
    
    def __init__(self):
        """Initialize GitHub Secrets handler."""
        self.config = Config()
        self.api_url = self.config.get("github_api_url", "https://github-secrets.vercel.app/api/github-secrets")
    
    def upload_secrets(self, repo: str, pat: str, env_path: str) -> Dict[str, Any]:
        """
        Upload secrets from .env file to GitHub repository.
        Just forwards the file path to the API without parsing.
        
        Args:
            repo: GitHub repository in format 'username/repo-name'
            pat: GitHub Personal Access Token
            env_path: Path to .env file
            
        Returns:
            API response as dictionary
        """
        # Check if env file exists
        env_file = Path(env_path)
        if not env_file.exists():
            return {
                "success": False,
                "error": f"Environment file not found: {env_path}"
            }
        
        try:
            # Prepare the multipart form data
            files = {
                'repo': (None, repo),
                'pat': (None, pat),
                'env': (env_file.name, open(env_file, 'rb'), 'text/plain')
            }
            
            # Make the API request
            response = requests.post(
                self.api_url,
                files=files
            )
            
            # Close the file
            files['env'][1].close()
            
            # Parse the response
            try:
                json_response = response.json()
                return json_response
            except ValueError:
                return {
                    "success": False,
                    "error": f"Invalid JSON response: {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }