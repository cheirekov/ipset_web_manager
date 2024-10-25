# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ipset \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user to run the app
RUN useradd -ms /bin/bash flaskuser

# Set the working directory to /app
WORKDIR /app

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Grant sudo permissions for ipset to the flaskuser
RUN echo "flaskuser ALL=(ALL) NOPASSWD: /sbin/ipset" >> /etc/sudoers

# Change ownership of the app directory to flaskuser
RUN chown -R flaskuser:flaskuser /app

# Switch to the non-root user
USER flaskuser

# Expose the port the app runs on
EXPOSE 3300

# Run the application
CMD ["python", "ipset_manager.py"]

