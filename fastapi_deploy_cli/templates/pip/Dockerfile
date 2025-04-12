FROM python:3.12-slim-bookworm

WORKDIR /app

# Define build arguments with default values
ARG APP_NAME
ARG DEBUG_MODE
ARG API_VERSION
ARG ENVIRONMENT
ARG PORT
ARG BUILD_ENV="production"

# Set build-time environment variables
ENV APP_NAME=$APP_NAME \
    DEBUG_MODE=$DEBUG_MODE \
    API_VERSION=$API_VERSION \
    ENVIRONMENT=$ENVIRONMENT \
    PORT=$PORT \
    BUILD_ENV=$BUILD_ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install dependencies directly in the final image
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    # Verify uvicorn is installed and show its location
    which uvicorn || echo "uvicorn not found" && \
    pip list | grep uvicorn

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy application code
COPY --chown=appuser:appuser ./main.py ./main.py

# Use non-root user
USER appuser

# Command to run the application using python -m instead of direct executable
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]