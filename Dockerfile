# Use an official Python runtime as a parent image, specifying the required platform.
# Using a slim image is good practice for smaller final image sizes.
FROM --platform=linux/amd64 python:3.9-slim

# Set environment variables to prevent Python from writing .pyc files and to run in unbuffered mode.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container.
WORKDIR /app

# Copy the dependencies file to the working directory.
COPY requirements.txt .

# Install the Python dependencies from requirements.txt.
# This step requires an internet connection during the build process.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire local 'src' directory (which includes main.py, config.py, etc.)
# into the '/app/src' directory in the container.
COPY ./src ./src

# --- Model Handling Note ---
# The model is no longer copied directly into the image.
# Instead, the sentence-transformers library will automatically download and cache
# the model into the container's filesystem the first time the application is run.
# This requires the container to have internet access on its first execution.
# Subsequent runs will use the local cache and can be performed offline.

# Command to run the application.
CMD ["python", "-m", "src.main"]
