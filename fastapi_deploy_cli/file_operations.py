"""
File operations for FastAPI Deploy CLI.
"""
import re
from pathlib import Path
from typing import Dict, Any, Optional, List

from fastapi_deploy_cli.config import Config
from fastapi_deploy_cli.env_handler import EnvHandler

class FileOps:
    """Handles file operations for deployment setup."""
    
    def __init__(self, package_manager: str = "uv", env_path: str = ".env", github_variables: List[str] = None,
                 domain: str = "domain.example.com", port: str = "8001", branch_name: str = "main", production_branch: bool = False,
        production_domain: Optional[str] = None, production_port: Optional[str] = None):
        """
        Initialize file operations.
        
        Args:
            package_manager: Package manager to use ('pip' or 'uv')
            env_path: Path to .env file
            github_variables: List of variables added to GitHub secrets
            domain: Application domain
            port: Application port
            branch_name: Name of the branch
            production_branch: Whether to set up a production branch
            production_domain: Domain for production deployment (if production_branch is True)
            production_port: Port for production deployment (if production_branch is True)
        """
        self.package_manager = package_manager
        self.env_path = env_path
        self.config = Config()
        self.templates_dir = self.config.get_templates_dir()
        self.github_variables = github_variables or []
        self.domain = domain
        self.port = port
        self.branch_name = branch_name
        self.production_branch = production_branch
        self.production_domain = production_domain if production_branch else None
        self.production_port = production_port if production_branch else None
        
        # Load environment variables if file exists
        self.env_handler = EnvHandler(env_path)
        
        # Define essential deployment variables that are not to be modified
        self.deployment_vars = ["SERVER_HOST", "SERVER_USER", "SSH_PRIVATE_KEY", "PAT"]
        
        # Get additional variables (excluding deployment vars)
        self.additional_vars = [var for var in self.github_variables if var not in self.deployment_vars]
        
        # Ensure the .github/workflows directory exists
        self.github_dir = Path(".github")
        self.workflows_dir = self.github_dir / "workflows"
        
        if not self.github_dir.exists():
            self.github_dir.mkdir(exist_ok=True)
        
        if not self.workflows_dir.exists():
            self.workflows_dir.mkdir(exist_ok=True)
    
    def _get_template_path(self, file_name: str) -> Path:
        """
        Get template file path.
        
        Args:
            file_name: Template file name
            
        Returns:
            Path to template file
        """
        return self.templates_dir / self.package_manager / file_name
    
    def _modify_dockerfile(self, content: str) -> str:
        """
        Modify Dockerfile content to include all environment variables.
        
        Args:
            content: Original Dockerfile content
            
        Returns:
            Modified Dockerfile content
        """
        # Update the CMD port
        if self.package_manager == "uv":
            # Update CMD port for uv
            cmd_pattern = r'CMD \["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"\]'
            content = re.sub(cmd_pattern, f'CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{self.port}"]', content)
        else:
            # Update CMD port for pip
            cmd_pattern = r'CMD \["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"\]'
            content = re.sub(cmd_pattern, f'CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{self.port}"]', content)
        
        if not self.additional_vars:
            return content
        
        # Create ARG declarations
        arg_declarations = "\n".join([f"ARG {var}" for var in self.additional_vars])
        
        # Create ENV variables
        env_vars = " \\\n    ".join([f"{var}=${var}" for var in self.additional_vars])
        
        if self.package_manager == "uv":
            # Add ARGs to initial build stage
            if "# Define build arguments with default values" in content:
                # Find the position to insert the ARGs
                args_index = content.find("# Define build arguments with default values")
                args_end_index = content.find("\n", args_index)
                
                # Insert standard args and additional args after the comment line
                new_content = content[:args_end_index+1] + "\n" + arg_declarations + "\n" + content[args_end_index+1:]
                content = new_content
                    
            # Add ENV variables to initial build stage
            if "# Set build-time environment variables" in content:
                # Find the position to insert the ENV variables
                env_index = content.find("# Set build-time environment variables")
                env_end_index = content.find("\n", env_index)
                
                # Find where to insert ENV declaration
                if "ENV" in content[env_end_index:env_end_index + 100]:
                    # ENV already exists, we'll modify it
                    env_start = content.find("ENV", env_end_index)
                    env_end = content.find("\n\n", env_start)
                    if env_end == -1:  # If not found, search for next section
                        env_end = content.find("\n#", env_start)
                    if env_end == -1:  # If still not found, go to end of content
                        env_end = len(content)
                        
                    # Create new ENV content
                    env_content = content[env_start:env_end].strip()
                    new_env_content = env_content + " \\\n    " + env_vars
                    
                    # Replace old ENV with new one
                    content = content.replace(env_content, new_env_content)
                else:
                    # No ENV exists, add new one
                    new_content = content[:env_end_index+1] + "\nENV " + env_vars + "\n" + content[env_end_index+1:]
                    content = new_content
                    
            # Add ARGs to final stage
            if "# Define build arguments again for the final stage" in content:
                # Find the position to insert the ARGs
                args_index = content.find("# Define build arguments again for the final stage")
                args_end_index = content.find("\n", args_index)
                
                # Insert standard args and additional args after the comment line
                new_content = content[:args_end_index+1] + "\n" + arg_declarations + "\n" + content[args_end_index+1:]
                content = new_content
            
            # Add ENV variables to final stage
            if "# Set environment variables for runtime" in content:
                # Find the position to insert the ENV variables
                env_index = content.find("# Set environment variables for runtime")
                env_end_index = content.find("\n", env_index)
                
                # Find where to insert ENV declaration
                if "ENV" in content[env_end_index:env_end_index + 100]:
                    # ENV already exists, we'll modify it
                    env_start = content.find("ENV", env_end_index)
                    env_end = content.find("\n\n", env_start)
                    if env_end == -1:  # If not found, search for next section
                        env_end = content.find("\n#", env_start)
                        if env_end == -1:  # If still not found, search for WORKDIR
                            env_end = content.find("WORKDIR", env_start)
                    if env_end == -1:  # If still not found, go to end of content
                        env_end = len(content)
                        
                    # Create new ENV content
                    env_content = content[env_start:env_end].strip()

                    # Check for and fix double backslash
                    if "\\ \\" in env_content:
                        env_content = env_content.replace("\\ \\", "\\")
                    
                    new_env_content = env_content + " \\\n    " + env_vars
                    
                    # Replace old ENV with new one
                    content = content.replace(env_content, new_env_content)
                else:
                    # No ENV exists, add new one
                    new_content = content[:env_end_index+1] + "\nENV " + env_vars + "\n" + content[env_end_index+1:]
                    content = new_content
                    
        else:  # pip
            # Add ARGs to define section
            if "# Define build arguments with default values" in content:
                # Find the position to insert the ARGs
                args_index = content.find("# Define build arguments with default values")
                args_end_index = content.find("\n", args_index)
                
                # Insert standard args and additional args after the comment line
                new_content = content[:args_end_index+1] + "\n" + arg_declarations + "\n" + content[args_end_index+1:]
                content = new_content
                    
            # Add ENV variables to build-time section
            if "# Set build-time environment variables" in content:
                # Find the position to insert the ENV variables
                env_index = content.find("# Set build-time environment variables")
                env_end_index = content.find("\n", env_index)
                
                # Find where to insert ENV declaration
                if "ENV" in content[env_end_index:env_end_index + 100]:
                    # ENV already exists, we'll modify it
                    env_start = content.find("ENV", env_end_index)
                    env_end = content.find("\n\n", env_start)
                    if env_end == -1:  # If not found, search for next section
                        env_end = content.find("\n#", env_start)
                        if env_end == -1:  # If still not found, search for COPY
                            env_end = content.find("COPY", env_start)
                    if env_end == -1:  # If still not found, go to end of content
                        env_end = len(content)
                        
                    # Create new ENV content
                    env_content = content[env_start:env_end].strip()
                    new_env_content = env_content + " \\\n    " + env_vars
                    
                    # Replace old ENV with new one
                    content = content.replace(env_content, new_env_content)
                else:
                    # No ENV exists, add new one
                    new_content = content[:env_end_index+1] + "\nENV " + env_vars + "\n" + content[env_end_index+1:]
                    content = new_content
        
        return content
    
    def _modify_docker_compose(self, content: str) -> str:
        """
        Modify docker-compose.yml content to include custom domain, port, and all environment variables.
        
        Args:
            content: Original docker-compose.yml content
            
        Returns:
            Modified docker-compose.yml content
        """
        # Replace domain.example.com with the custom domain
        content = content.replace("domain.example.com", self.domain)
        
        # Replace port 8001 with the custom port in all places
        content = re.sub(r'(\s*-\s*)"8001:8000"', f'\\1"{self.port}:8000"', content)
        content = re.sub(r'(\s*-\s*)"traefik\.http\.services\.\${COMPOSE_PROJECT_NAME:-app}\.loadbalancer\.server\.port=8001"', 
                        f'\\1"traefik.http.services.${{COMPOSE_PROJECT_NAME:-app}}.loadbalancer.server.port={self.port}"', 
                        content)
        
        if not self.additional_vars:
            return content
            
        # Add additional variables to build args
        if "args:" in content:
            args_pattern = r"(args:(?:\s*-[^\n]*)*)"
            arg_lines = "\n" + "\n".join([f"        - {var}=${{{var}}}" for var in self.additional_vars])
            
            content = re.sub(
                args_pattern,
                f"\\1{arg_lines}",
                content
            )
        
        # Add additional variables to environment section
        if "environment:" in content:
            env_pattern = r"(environment:(?:\s*-[^\n]*)*)"
            env_lines = "\n" + "\n".join([f"      - {var}=${{{var}}}" for var in self.additional_vars])
            
            content = re.sub(
                env_pattern,
                f"\\1{env_lines}",
                content
            )
        
        return content
    
    def _modify_workflow(self, content: str) -> str:
        """
        Modify GitHub Actions workflow content to include all environment variables
        and add production branch support if enabled.
        
        Args:
            content: Original workflow content
            
        Returns:
            Modified workflow content
        """
        # Replace main with the specified branch name
        content = re.sub(r'branches: \[ main(?:, [^\]]+)? \]', f'branches: [ {self.branch_name} ]', content)
        
        # Add environment variables to env section
        if not self.additional_vars and not self.production_branch:
            return content
            
        if "env:" in content:
            env_pattern = r"(env:(?:\s*[A-Z_]+:[^\n]*)*)"
            env_lines = "\n" + "\n".join([f"          {var}: ${{{{ secrets.{var} }}}}" for var in self.additional_vars])
            
            content = re.sub(
                env_pattern,
                f"\\1{env_lines}",
                content
            )
        
        # Add variables to envs parameter
        if "envs:" in content:
            envs_pattern = r"(envs:\s*[^,\n]*(?:,[^,\n]*)*)"
            additional_envs = "," + ",".join(self.additional_vars)
            
            content = re.sub(
                envs_pattern,
                f"\\1{additional_envs}",
                content
            )
        
        # Add export statements
        if "# Export environment variables" in content:
            export_pattern = r"(# Export environment variables\s*\n(?:\s*export [A-Z_]+=[^\n]*\n)*)"
            export_lines = "\n".join([f'            export {var}="${{{var}}}"' for var in self.additional_vars])
            
            content = re.sub(
                export_pattern,
                f"\\1{export_lines}\n",
                content
            )
        
        # Add unset statements
        if "# Clear environment variables" in content:
            unset_pattern = r"(# Clear environment variables\s*\n(?:\s*unset [A-Z_]+\n)*)"
            unset_lines = "\n".join([f"            unset {var}" for var in self.additional_vars])
            
            content = re.sub(
                unset_pattern,
                f"\\1{unset_lines}\n",
                content
            )
        
        # Add production branch job if needed
        if self.production_branch and "create-pr:" not in content:
            # Find the end of the deploy job
            deploy_job_end = content.find("  # Clear environment variables\n            unset COMPOSE_PROJECT_NAME")
            if deploy_job_end != -1:
                deploy_job_end = content.find("\n", deploy_job_end + 60)  # Move past the unset line
                
                # Add the create-pr job
                create_pr_job = f"""

  create-pr:
    needs: deploy
    runs-on: ubuntu-latest
    steps:
      - name: Checkout {self.branch_name}
        uses: actions/checkout@v3
        with:
          ref: {self.branch_name}
          token: ${{{{ secrets.PAT }}}}
      
      - name: Set up Git
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
      
      - name: Check if prod branch exists
        id: check-branch
        run: |
          if git ls-remote --heads origin prod | grep prod; then
            echo "exists=true" >> $GITHUB_OUTPUT
          else
            echo "exists=false" >> $GITHUB_OUTPUT
          fi
      
      - name: Create prod branch if it doesn't exist
        if: steps.check-branch.outputs.exists == 'false'
        run: |
          git checkout -b prod
          git push origin prod
      
      - name: Modify docker-compose for production
        id: modify-domain
        run: |
          # Update the domain in docker-compose.yml to production
          if [ -f "docker-compose.yml" ]; then
            # Replace test domain with production domain
            sed -i 's/`{self.domain}`/`{self.production_domain}`/g' docker-compose.yml
            
            # Update the port from {self.port}:8000 to {self.production_port}:8000 for production
            sed -i 's/"{self.port}:8000"/"{self.production_port}:8000"/g' docker-compose.yml
             
            # Update the traefik service port from {self.port} to {self.production_port}
            sed -i 's/loadbalancer\\.server\\.port={self.port}/loadbalancer.server.port={self.production_port}/g' docker-compose.yml
            
            # Check if the file was actually modified
            if git diff --quiet docker-compose.yml; then
              echo "No changes found in docker-compose.yml"
              echo "changes_made=false" >> $GITHUB_OUTPUT
            else
              echo "Domain and port updated to production in docker-compose.yml"
              echo "changes_made=true" >> $GITHUB_OUTPUT
            fi
          else
            echo "docker-compose.yml not found!"
            echo "changes_made=false" >> $GITHUB_OUTPUT
            exit 1
          fi
      
      - name: Create PR for domain changes
        if: steps.modify-domain.outputs.changes_made == 'true'
        uses: peter-evans/create-pull-request@v4
        with:
          token: ${{{{ secrets.PAT }}}}
          commit-message: Update domain and port for production
          title: Deploy to Production
          body: |
            This PR updates the configuration for production deployment:
            
            - Changed domain to production ({self.production_domain})
            - Updated port mapping from {self.port}:8000 to {self.production_port}:8000
            
            This PR was automatically created after a successful test deployment.
          branch: update-to-prod
          branch-suffix: timestamp
          delete-branch: true
          base: prod
          
      - name: Fetch prod branch for comparison
        run: |
          git fetch origin prod || true
          
      - name: Check for code changes beyond domain
        id: check-changes
        run: |
          if git ls-remote --heads origin prod | grep -q prod; then
            # Compare {self.branch_name} and prod branches excluding docker-compose.yml
            OTHER_CHANGES=$(git diff --name-only origin/{self.branch_name} origin/prod | grep -v "docker-compose.yml" || true)
            
            if [ -n "$OTHER_CHANGES" ]; then
              echo "Other files have changes beyond docker-compose.yml"
              echo "has_other_changes=true" >> $GITHUB_OUTPUT
              echo "CHANGED_FILES<<EOF" >> $GITHUB_ENV
              echo "$OTHER_CHANGES" >> $GITHUB_ENV
              echo "EOF" >> $GITHUB_ENV
            else
              echo "No other changes between branches beyond docker-compose.yml"
              echo "has_other_changes=false" >> $GITHUB_OUTPUT
            fi
          else
            echo "Prod branch doesn't exist yet for comparison"
            echo "has_other_changes=false" >> $GITHUB_OUTPUT
          fi
      
      - name: Create PR with all code changes
        if: steps.check-changes.outputs.has_other_changes == 'true'
        uses: peter-evans/create-pull-request@v4
        with:
          token: ${{{{ secrets.PAT }}}}
          commit-message: Sync all changes from {self.branch_name} to prod
          title: Sync all changes from {self.branch_name} to production
          body: |
            This PR includes all changes from {self.branch_name} branch ready for production deployment.
            
            Changed files include:
            ${{{{ env.CHANGED_FILES }}}}
          branch: sync-all-changes
          branch-suffix: timestamp
          delete-branch: true
          base: prod
"""
                content = content[:deploy_job_end+1] + create_pr_job
        
        return content
    
    def _modify_production_workflow(self, content: str) -> str:
        """
        Modify GitHub Actions production workflow content.
        
        Args:
            content: Original workflow content
            
        Returns:
            Modified workflow content
        """
        # Add environment variables to env section
        if not self.additional_vars and not self.production_branch:
            return content
            
        if "env:" in content:
            env_pattern = r"(env:(?:\s*[A-Z_]+:[^\n]*)*)"
            env_lines = "\n" + "\n".join([f"          {var}: ${{{{ secrets.{var} }}}}" for var in self.additional_vars])
            
            content = re.sub(
                env_pattern,
                f"\\1{env_lines}",
                content
            )
        
        # Add variables to envs parameter
        if "envs:" in content:
            envs_pattern = r"(envs:\s*[^,\n]*(?:,[^,\n]*)*)"
            additional_envs = "," + ",".join(self.additional_vars)
            
            content = re.sub(
                envs_pattern,
                f"\\1{additional_envs}",
                content
            )
        
        # Add export statements
        if "# Export environment variables" in content:
            export_pattern = r"(# Export environment variables\s*\n(?:\s*export [A-Z_]+=[^\n]*\n)*)"
            export_lines = "\n".join([f'            export {var}="${{{var}}}"' for var in self.additional_vars])
            
            content = re.sub(
                export_pattern,
                f"\\1{export_lines}\n",
                content
            )
        
        # Add unset statements
        if "# Clear environment variables" in content:
            unset_pattern = r"(# Clear environment variables\s*\n(?:\s*unset [A-Z_]+\n)*)"
            unset_lines = "\n".join([f"            unset {var}" for var in self.additional_vars])
            
            content = re.sub(
                unset_pattern,
                f"\\1{unset_lines}\n",
                content
            )
        return content
    
    def _copy_and_modify_template(self, template_name: str, target_path: Path, modifier_func=None) -> bool:
        """
        Copy template file to target path and modify if needed.
        
        Args:
            template_name: Template file name
            target_path: Target file path
            modifier_func: Function to modify the template content
            
        Returns:
            True if successful, False otherwise
        """
        template_path = self._get_template_path(template_name)
        
        try:
            # Read template content
            with open(template_path, 'r') as f:
                content = f.read()
            
            # Modify content if modifier function is provided
            if modifier_func:
                content = modifier_func(content)
            
            # Write content to target path
            with open(target_path, 'w') as f:
                f.write(content)
            
            return True
        except Exception as e:
            print(f"Error processing template {template_name}: {e}")
            return False
    
    def setup_dockerfile(self) -> bool:
        """
        Set up Dockerfile with all environment variables.
        
        Returns:
            True if successful, False otherwise
        """
        return self._copy_and_modify_template("Dockerfile", Path("Dockerfile"), self._modify_dockerfile)
    
    def setup_docker_compose(self) -> bool:
        """
        Set up docker-compose.yml with all environment variables.
        
        Returns:
            True if successful, False otherwise
        """
        return self._copy_and_modify_template("docker-compose.yml", Path("docker-compose.yml"), self._modify_docker_compose)
    
    def setup_github_workflow(self) -> bool:
        """
        Set up GitHub Actions workflow file with all environment variables.
        
        Returns:
            True if successful, False otherwise
        """
        workflow_path = self.workflows_dir / "deploy.yml"
        return self._copy_and_modify_template("deploy.yml", workflow_path, self._modify_workflow)
    
    def setup_production_workflow(self) -> bool:
        """
        Set up GitHub Actions production workflow file with all environment variables.
        
        Returns:
            True if successful, False otherwise
        """
        workflow_path = self.workflows_dir / "deploy-prod.yml"
        return self._copy_and_modify_template("deploy-prod.yml", workflow_path, self._modify_production_workflow)