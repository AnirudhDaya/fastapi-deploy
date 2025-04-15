# FastAPI Deploy CLI

A command-line tool for setting up automated deployment of FastAPI applications using Docker, Docker Compose, and GitHub Actions.

## Features

- Supports both pip and uv package managers
- Configures GitHub Actions for CI/CD
- Support for separate test and production environments
- Automatic PR creation from test to production
- Automatically sets up GitHub secrets for deployment
- Creates Dockerfile and docker-compose.yml files
- Sets up secure deployment with Traefik
- Custom domain and port configuration
- Dynamic environment variable handling
- Interactive CLI with arrow key selection

## Installation

```bash
# Install from PyPI
pip install fastapi-deploy-cli

# Or using uv
uv pip install fastapi-deploy-cli

# Or install from source
git clone https://github.com/your-username/fastapi-deploy-cli.git
cd fastapi-deploy-cli
pip install -e .
```

## Usage

### Initialize a new deployment setup

```bash
# Navigate to your FastAPI project directory
cd your-fastapi-project

# Run the initialization command
fastapi-deploy init
```

The CLI will guide you through the setup process:

1. Choose your package manager (pip or uv) using arrow keys
2. Specify the path to your .env file
3. Configure application domain and port
4. Set up production environment (optional)
5. Set up GitHub repository and Personal Access Token
6. Add secrets to GitHub repository
7. Create necessary deployment files

### Update deployment files

```bash
fastapi-deploy update
```

The update command allows you to:
1. Change your package manager
2. Update your domain and port settings
3. Update GitHub secrets
4. Refresh deployment files with the latest configurations

## Required Environment Variables

Before using the CLI, create an .env file with the following variables:

```
SERVER_HOST=your-server-hostname
SERVER_USER=your-server-username
SSH_PRIVATE_KEY=your-private-key
PAT=your-github-personal-access-token  # Required for production branch automation
```

Additional environment variables will be automatically detected and included in deployment files.

## Domain and Port Configuration

The CLI prompts you to specify:
- Application domain (e.g., `api.example.com`)
- Application port (e.g., `8001`)

If production environment is enabled:
- Production domain (e.g., `prod-api.example.com`)
- Production port (e.g., `8002`)

These settings are automatically applied to:
- Docker Compose configuration
- Dockerfile CMD command
- Traefik routing settings

## GitHub Actions Workflow

### Standard Deployment

The CLI sets up a GitHub Actions workflow that:

1. Checks out your code
2. Prepares files for deployment
3. Copies files to your server via SSH
4. Builds and starts Docker containers
5. Performs cleanup

### Production Deployment (Optional)

When enabled, the production deployment workflow:

1. Performs standard deployment to test environment
2. Creates or updates a production branch
3. Generates a Pull Request with domain and port changes for production
4. When merged, deploys to production environment

This creates a proper CI/CD pipeline with test-to-production promotion via PR review.

## Requirements

- Python 3.8+
- A FastAPI application
- A GitHub repository
- A GitHub Personal Access Token with repo and workflow scopes
- A server with SSH access and Docker installed
- Traefik running on your server (for routing)

## License

MIT