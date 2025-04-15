#!/usr/bin/env python3
"""
FastAPI Deploy CLI - A tool for deploying FastAPI applications with ease.
"""
import click
import questionary
from questionary import Style
from rich.console import Console
from rich.prompt import Prompt

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
    
    # Step 2.5: Collect additional application settings
    console.print("\n[bold]Step 2.5:[/bold] Application settings")
    
    # Ask for domain
    domain = Prompt.ask(
        "Enter domain for your application",
        default="app.example.com"
    )
    
    # Ask for port
    port = Prompt.ask(
        "Enter the port for your application",
        default="8001"
    )
    
    # Ask for branch name
    branch_name = Prompt.ask(
        "Enter the branch name for your application",
        default="main"
    )

    # Ask if user wants a production branch
    console.print("\n[bold]Step 2.6:[/bold] Branch configuration")
    production_branch = questionary.confirm(
        "Do you want to set up a production branch?",
        default=True,
        style=get_questionary_style()
    ).ask()
    
    # Initialize production-specific variables
    prod_domain = None
    prod_port = None
    
    if production_branch:      
        # Ask for production domain
        prod_domain = Prompt.ask(
            "Enter domain for your production deployment",
            default=f"prod-{domain}"
        )
        
        # Ask for production port
        prod_port = Prompt.ask(
            "Enter the port for your production deployment",
            default="8002"
        )
        
        console.print(f"[green]Production branch will be configured with domain '{prod_domain}' on port {prod_port}[/green]")
    else:
        console.print("[yellow]No production branch will be configured[/yellow]")

    console.print(f"[green]Updated environment file with domain and port settings[/green]")
    
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
    file_ops = FileOps(
        package_manager, 
        env_path, 
        variables, 
        domain, 
        port, 
        branch_name,
        production_branch=production_branch,
        production_domain=prod_domain,
        production_port=prod_port
    )
    
    # Create necessary files
    dockerfile_result = file_ops.setup_dockerfile()
    compose_result = file_ops.setup_docker_compose()
    workflow_result = file_ops.setup_github_workflow()
    prod_workflow_result = file_ops.setup_production_workflow()
    
    # Complete
    console.print("\n[bold green]Setup Complete![/bold green]")
    
    # Show summary
    console.print("\n[bold]Summary:[/bold]")
    console.print(f"🔧 Package manager: [cyan]{package_manager}[/cyan]")
    console.print(f"📄 Environment file: [cyan]{env_path}[/cyan]")
    console.print(f"🌐 Domain: [cyan]{domain}[/cyan]")
    console.print(f"🔌 Port: [cyan]{port}[/cyan]")
    console.print(f"🔗 GitHub repository: [cyan]{repo}[/cyan]")
    console.print(f"🌿 Production branch: [cyan]{'Yes - ' if production_branch else 'No'}[/cyan]")
    console.print(f"🔒 GitHub secrets uploaded: [cyan]{'✓' if result.get('success', False) else '✗'}[/cyan]")
    console.print(f"📦 Created deployment files:")
    console.print(f"   - [cyan]Dockerfile[/cyan] {'✓' if dockerfile_result else '✗'}")
    console.print(f"   - [cyan]docker-compose.yml[/cyan] {'✓' if compose_result else '✗'}")
    console.print(f"   - [cyan].github/workflows/deploy.yml[/cyan] {'✓' if workflow_result else '✗'}")
    console.print(f"   - [cyan].github/workflows/deploy-prod.yml[/cyan] {'✓' if prod_workflow_result else '✗'}")

    # Next steps
    console.print("\n[bold]Next steps:[/bold]")
    console.print("1. Commit and push your code to GitHub 🚀")
    console.print("2. Monitor GitHub Actions for deployment progress 📊")
    console.print("3. Your app will be deployed to your server automatically 🎉\n")

if __name__ == "__main__":
    cli()