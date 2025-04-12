# FastAPI Deploy CLI

A command-line tool for setting up automated deployment of FastAPI applications using Docker, Docker Compose, and GitHub Actions.

## Features

- Supports both pip and uv package managers
- Configures GitHub Actions for CI/CD
- Automatically sets up GitHub secrets for deployment
- Copies Dockerfile and docker-compose.yml files
- Sets up secure deployment with traefik
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
3. Set up GitHub repository and Personal Access Token
4. Add secrets to GitHub repository
5. Create necessary deployment files

### Update deployment files

```bash
fastapi-deploy update
```

## Required Environment Variables

Before using the CLI, create an .env file with the following variables:

```
SERVER_HOST=your-server-hostname
SERVER_USER=your-server-username
SSH_PRIVATE_KEY=your-private-key
APP_NAME=your-app-name
DEBUG_MODE=False
API_VERSION=v1
ENVIRONMENT=production
PORT=8001
```

## GitHub Actions Workflow

The CLI sets up a GitHub Actions workflow that:

1. Checks out your code
2. Prepares files for deployment
3. Copies files to your server via SSH
4. Builds and starts Docker containers
5. Performs cleanup

## License

MIT
# FastAPI Deploy CLI

A command-line tool for setting up automated deployment of FastAPI applications using Docker, Docker Compose, and GitHub Actions.

## Features

- Supports both pip and uv package managers
- Configures GitHub Actions for CI/CD
- Automatically sets up GitHub secrets for deployment
- Creates Dockerfile and docker-compose.yml files
- Sets up secure deployment with traefik

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

1. Choose your package manager (pip or uv)
2. Configure environment variables
3. Set up GitHub repository and Personal Access Token
4. Add secrets to GitHub repository
5. Create necessary deployment files

### Update deployment files

```bash
fastapi-deploy update
```

## Requirements

- Python 3.8+
- A FastAPI application
- A GitHub repository
- A GitHub Personal Access Token with repo scope
- A server with SSH access and Docker installed

## Environment Variables

The CLI will help you set up the following environment variables:

- `SERVER_HOST`: SSH host for deployment
- `SERVER_USER`: SSH username for deployment
- `SSH_PRIVATE_KEY`: SSH private key for deployment
- `APP_NAME`: Your application name
- `DEBUG_MODE`: Debug mode (True/False)
- `API_VERSION`: API version (e.g., v1)
- `ENVIRONMENT`: Deployment environment (e.g., production, staging)
- `PORT`: Application port

## GitHub Actions Workflow

The CLI sets up a GitHub Actions workflow that:

1. Checks out your code
2. Prepares files for deployment
3. Copies files to your server via SSH
4. Builds and starts Docker containers
5. Performs cleanup

## License

MIT