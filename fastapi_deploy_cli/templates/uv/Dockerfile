# Build stage
FROM python:3.12-slim-bookworm AS builder

# Copy UV binary from official image
COPY --from=ghcr.io/astral-sh/uv:0.6.13 /uv /uvx /bin/

WORKDIR /app

# Define build arguments with default values

# Set build-time environment variables

# Copy only files needed for dependency installation
COPY pyproject.toml ./

# Install dependencies with UV sync
RUN uv sync

# Copy the application code
COPY . .

# Final lightweight runtime stage
FROM python:3.12-slim-bookworm

# Create a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Define build arguments again for the final stage

# Set environment variables for runtime
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application files
COPY --chown=appuser:appuser ./main.py ./main.py

# Switch to non-root user
USER appuser

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]