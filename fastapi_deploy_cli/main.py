#!/usr/bin/env python3
"""
FastAPI Deploy CLI - A tool for deploying FastAPI applications with ease.
"""
import os
import sys
from pathlib import Path

import click
import questionary
from questionary import Style
from rich.console import Console
from rich.prompt import Prompt, Confirm

from fastapi_deploy_cli.config import Config
from fastapi_deploy_cli.env_handler import EnvHandler
from fastapi_deploy_cli.github_api import GithubSecrets
from fastapi_deploy_cli.file_operations import FileOps
from fastapi_deploy_cli.utils import validate_github_repo, validate_pat

console = Console()

def get_questionary_style():
    """Return a consistent style for questionary prompts."""
    return Style([
        ('qmark', 'fg:cyan bold'),        # Question mark
        ('question', 'bold'),             # Question text
        ('answer', 'fg:green bold'),      # Answer text
        ('pointer', 'fg:cyan bold'),      # Selection pointer
        ('highlighted', 'fg:cyan bold'),  # Highlighted option
        ('selected', 'fg:green bold'),    # Selected option
    ])

@click.group()
def cli():
    """FastAPI Deploy CLI - A tool for deploying FastAPI applications."""
    pass

@cli.command()
def init():
    """Initialize deployment setup for a FastAPI application."""
    console.print("\n[bold blue]FastAPI Deploy CLI[/bold blue] - Setup your deployment configuration\n")
    
    # Step 1: Choose the package manager
    console.print("[bold]Step 1:[/bold] Choose your package manager:")
    
    package_manager = questionary.select(
        "Select package manager:",
        choices=["pip", "uv"],
        default="uv",
        style=get_questionary_style()
    ).ask()
    
    # Step 2: Setup env file
    console.print("\n[bold]Step 2:[/bold] Environment file configuration")
    env_path = Prompt.ask(
        "Enter path to your .env file",
        default=".env"
    )
    
    env_handler = EnvHandler(env_path)
    
    if not env_handler.file_exists():
        console.print(f"[yellow]No .env file found at {env_path}.[/yellow]")
        console.print("[yellow]Please create an .env file at the specified path with the following variables:[/yellow]")
        console.print("""
Required environment variables:
- SERVER_HOST: SSH host for GitHub Actions
- SERVER_USER: SSH username for GitHub Actions
- SSH_PRIVATE_KEY: SSH private key for GitHub Actions
- APP_NAME: Your application name
- DEBUG_MODE: Debug mode (True/False)
- API_VERSION: API version (e.g., v1)
- ENVIRONMENT: Deployment environment (e.g., production)
- PORT: Application port
        """)
        
        if not questionary.confirm(
            "Continue after creating the .env file?", 
            default=True,
            style=get_questionary_style()
        ).ask():
            console.print("[red]Setup cancelled.[/red]")
            return
    else:
        console.print(f"[green]Found .env file at {env_path}[/green]")
        # Check if required variables are present
        missing_vars = env_handler.check_required_vars([
            "SERVER_HOST", "SERVER_USER", "SSH_PRIVATE_KEY"
        ])
        
        if missing_vars:
            console.print(f"[yellow]The following required variables are missing in your .env file:[/yellow]")
            for var in missing_vars:
                console.print(f"- {var}")
            
            console.print("[yellow]Please add these variables to your .env file before continuing.[/yellow]")
            
            if not questionary.confirm(
                "Continue after updating the .env file?", 
                default=True,
                style=get_questionary_style()
            ).ask():
                console.print("[red]Setup cancelled.[/red]")
                return
    
    # Step 3: Get GitHub repository info
    console.print("\n[bold]Step 3:[/bold] GitHub repository configuration")
    
    # Prompt for GitHub repository with validation
    while True:
        repo = Prompt.ask("Enter GitHub repository in format 'username/repo-name'")
        if validate_github_repo(repo):
            break
        else:
            console.print("[red]Repository must be in format 'username/repo-name'[/red]")
    
    # Prompt for GitHub PAT with validation
    while True:
        pat = Prompt.ask("Enter GitHub Personal Access Token (PAT)")
        if validate_pat(pat):
            break
        else:
            console.print("[red]PAT should be at least 40 characters long[/red]")
    
    # Step 4: Add env to GitHub secrets
    console.print("\n[bold]Step 4:[/bold] Adding environment variables to GitHub secrets")
    github_secrets = GithubSecrets()
    result = github_secrets.upload_secrets(repo, pat, env_path)
    
    variables = []
    if result.get("success"):
        console.print("[green]Successfully added environment variables to GitHub secrets[/green]")
        variables = github_secrets.get_environment_variables(result)
        console.print(f"Variables added: [cyan]{', '.join(variables)}[/cyan]")
    else:
        console.print("[red]Failed to add environment variables to GitHub secrets[/red]")
        if "variables" in result:
            console.print(f"Failed variables: {', '.join(result['variables'])}")
        if "error" in result:
            console.print(f"Error: {result['error']}")
    
    # Step 5: Setup deployment files
    console.print("\n[bold]Step 5:[/bold] Setting up deployment files")
    file_ops = FileOps(package_manager, env_path, variables)
    
    # Create necessary files
    dockerfile_result = file_ops.setup_dockerfile()
    compose_result = file_ops.setup_docker_compose()
    workflow_result = file_ops.setup_github_workflow()
    
    # Complete
    console.print("\n[bold green]Setup Complete![/bold green]")
    
    # Show summary
    console.print("\n[bold]Summary:[/bold]")
    console.print(f"🔧 Package manager: [cyan]{package_manager}[/cyan]")
    console.print(f"📄 Environment file: [cyan]{env_path}[/cyan]")
    console.print(f"🔗 GitHub repository: [cyan]{repo}[/cyan]")
    console.print(f"🔒 GitHub secrets uploaded: [cyan]{'✓' if result.get('success', False) else '✗'}[/cyan]")
    console.print(f"📦 Created deployment files:")
    console.print(f"   - [cyan]Dockerfile[/cyan] {'✓' if dockerfile_result else '✗'}")
    console.print(f"   - [cyan]docker-compose.yml[/cyan] {'✓' if compose_result else '✗'}")
    console.print(f"   - [cyan].github/workflows/deploy.yml[/cyan] {'✓' if workflow_result else '✗'}")
    
    # Next steps
    console.print("\n[bold]Next steps:[/bold]")
    console.print("1. Commit and push your code to GitHub 🚀")
    console.print("2. Monitor GitHub Actions for deployment progress 📊")
    console.print("3. Your app will be deployed to your server automatically 🎉\n")

@cli.command()
def update():
    """Update deployment files."""
    console.print("\n[bold blue]FastAPI Deploy CLI[/bold blue] - Update your deployment configuration\n")
    
    # Choose the package manager
    package_manager = questionary.select(
        "Select package manager to update configuration for:",
        choices=["pip", "uv"],
        default="uv",
        style=get_questionary_style()
    ).ask()
    
    # Ask for environment file path
    env_path = Prompt.ask(
        "Enter path to your .env file",
        default=".env"
    )
    
    # Check if env file exists
    env_handler = EnvHandler(env_path)
    if not env_handler.file_exists():
        console.print(f"[yellow]Warning: No .env file found at {env_path}. Continuing anyway.[/yellow]")
    else:
        console.print(f"[green]Found .env file at {env_path}[/green]")
    
    # Create file operations handler
    # We'll pass an empty variables list - FileOps will handle the templates without additional vars
    file_ops = FileOps(package_manager, env_path)
    
    # Ask which files to update using questionary
    update_dockerfile = questionary.confirm(
        "Update Dockerfile?", 
        default=True,
        style=get_questionary_style()
    ).ask()
    
    update_compose = questionary.confirm(
        "Update docker-compose.yml?", 
        default=True,
        style=get_questionary_style()
    ).ask()
    
    update_workflow = questionary.confirm(
        "Update GitHub Actions workflow file?", 
        default=True,
        style=get_questionary_style()
    ).ask()
    
    # Update files as requested
    if update_dockerfile:
        file_ops.setup_dockerfile()
        console.print("[green]Updated Dockerfile[/green]")
    
    if update_compose:
        file_ops.setup_docker_compose()
        console.print("[green]Updated docker-compose.yml[/green]")
    
    if update_workflow:
        file_ops.setup_github_workflow()
        console.print("[green]Updated GitHub Actions workflow file[/green]")
    
    console.print("\n[bold green]Update Complete![/bold green]")

if __name__ == "__main__":
    cli()