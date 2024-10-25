# IPSet Manager with Web Interface and HTTPS Support

This project provides a web-based IPSet Manager application built with Flask, Dockerized for ease of deployment, and secured with HTTPS using Caddy as a reverse proxy. The application allows you to view, add, delete, flush, save, and restore IPSet entries through a user-friendly web interface with authentication.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Directory Structure](#directory-structure)
- [Getting Started](#getting-started)
  - [Clone the Repository](#clone-the-repository)
  - [Set Up the Environment](#set-up-the-environment)
  - [Generate a Hashed Password](#generate-a-hashed-password)
  - [Configure the Application](#configure-the-application)
- [Docker Configuration](#docker-configuration)
  - [Dockerfile](#dockerfile)
  - [Docker Compose](#docker-compose)
  - [Caddy Configuration](#caddy-configuration)
- [Running the Application](#running-the-application)
- [Accessing the Web Interface](#accessing-the-web-interface)
- [Usage](#usage)
  - [View IPSet Entries](#view-ipset-entries)
  - [Add Entry](#add-entry)
  - [Delete Entry](#delete-entry)
  - [Flush IPSet List](#flush-ipset-list)
  - [Save IPSet Configuration](#save-ipset-configuration)
  - [Restore IPSet Configuration](#restore-ipset-configuration)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Features

- **Web-Based Interface**: Manage IPSet entries through a user-friendly web interface.
- **Authentication**: Secure access with HTTP Basic Authentication.
- **HTTPS Support**: Traffic is encrypted using HTTPS provided by Caddy and Let's Encrypt.
- **IPSet Operations**:
  - View existing IPSet entries.
  - Add new entries to IPSet lists.
  - Delete individual entries.
  - Flush entire IPSet lists.
  - Save and download the current IPSet configuration.
  - Restore IPSet configuration from a file.

---

## Prerequisites

- **Docker** and **Docker Compose** installed on your system.
- **Domain Name**: A domain name pointing to your server's IP address (e.g., `ipset.example.com`).
- **Open Ports**:
  - **Port 443**: Must be open and accessible for HTTPS connections.
- **Host Considerations**:
  - **Port 80**: If port 80 is occupied (e.g., by Apache), the configuration uses the TLS-ALPN-01 challenge to obtain SSL certificates without needing port 80.

---

## Directory Structure


- Your project directory should have the following structure:

- ipset-manager/
- ├── Dockerfile
- ├── docker-compose.yml
- ├── Caddyfile
- ├── requirements.txt
- ├── ipset_manager.py
- └── README.md

## Getting Started
- Clone the Repository

Clone this repository to your local machine:

git clone https://github.com/cheirekov/ipset_web_manager.git

cd ipset-manager
Set Up the Environment
Ensure you have Docker and Docker Compose installed:

Docker: Install Docker
Docker Compose: Install Docker Compose
Generate a Hashed Password
Generate a hashed password for the admin user:

Create a Python script named generate_password_hash.py:


from werkzeug.security import generate_password_hash

password = input("Enter password to hash: ")
hash = generate_password_hash(password)
print(f"Hashed password: {hash}")
Run the script:


python generate_password_hash.py
Enter your desired password when prompted. Copy the hashed password output.

Configure the Application
Update ipset_manager.py:

Replace the users dictionary with your hashed password:

users = {
    "admin": "your_hashed_password_here"
}
Set Your Domain in Caddyfile:

Replace ipset.mikro.work with your actual domain in the Caddyfile.
Docker Configuration
Dockerfile
Create a Dockerfile with the following content:


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
Docker Compose
Create a docker-compose.yml file:

version: '3.3'

services:
  ipset:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ipset
    cap_add:
      - NET_ADMIN
    network_mode: host
    restart: unless-stopped

  caddy:
    image: caddy:latest
    container_name: caddy
    restart: unless-stopped
    ports:
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
      - caddy_config:/config
    depends_on:
      - ipset
    extra_hosts:
      - "host.docker.internal:host-gateway"

volumes:
  caddy_data:
  caddy_config:
Caddy Configuration
Create a Caddyfile with the following content:


ipset.example.com {
    tls {
        alpn http/1.1
    }
    reverse_proxy host.docker.internal:3300
}
Replace ipset.example.com with your actual domain.

Running the Application
Build and start the services using Docker Compose:


docker-compose up --build -d
This command will:

Build the Docker image for the IPSet Manager application.
Start both the ipset and caddy containers in detached mode.
Accessing the Web Interface
Open your web browser and navigate to:

https://ipset.example.com
Username: admin
Password: The plaintext password you entered when generating the hash.
Usage
View IPSet Entries
The main page displays a table of all current IPSet entries.
Use the search bar to filter entries by IP address or list name.
Add Entry
In the "Add Entry" section, enter the List Name and IP Address.
Click "Add" to add the entry.
If the list does not exist, it will be created automatically.
Delete Entry
Each entry in the table has a "Delete" button.
Click "Delete" to remove the entry from the IPSet list.
Flush IPSet List
In the "Flush IPSet List" section, enter the List Name you wish to flush.
Click "Flush" to delete all entries in the specified list.
Save IPSet Configuration
Click the "Save List" button to download the current IPSet configuration.
The file ipset_backup.ipset will be downloaded to your local machine.
Restore IPSet Configuration
In the "Restore List" section, click "Choose File" and select the ipset_backup.ipset file.
Click "Restore List" to restore the IPSet configuration.
Security Considerations
Authentication: Uses HTTP Basic Authentication. Ensure strong passwords are used.
HTTPS Encryption: All traffic is encrypted using HTTPS provided by Caddy and Let's Encrypt.
Permissions: The Dockerfile grants necessary permissions for ipset operations. Be cautious with sudo privileges.
Firewall: Ensure that only necessary ports are open (port 443 for HTTPS).
Updates: Regularly update Docker images and dependencies to receive security patches.
Troubleshooting
Cannot Access Web Interface:

Ensure both Docker containers are running: docker-compose ps.
Check that port 443 is open and accessible.
Verify DNS settings for your domain.
SSL Certificate Issues:

Check Caddy logs for errors: docker logs caddy.
Ensure that port 443 is not blocked by a firewall.
IPSet Entries Not Displayed:

Confirm that the ipset container is running with network_mode: host.
Ensure that the Flask application is running on port 3300.
Permission Denied Errors:

Verify that the flaskuser has the necessary sudo permissions.
Check the Dockerfile for correct configuration of sudoers.
Caddy Cannot Connect to IPSet Manager:

Ensure host.docker.internal is correctly resolved in the caddy container.
Use curl http://host.docker.internal:3300 inside the caddy container to test connectivity.
License
This project is licensed under the MIT License. See the LICENSE file for details.

Acknowledgments
Flask: https://flask.palletsprojects.com/
Caddy Server: https://caddyserver.com/
Docker: https://www.docker.com/
Let's Encrypt: https://letsencrypt.org/
Note: Use this application responsibly and ensure compliance with all applicable laws and regulations regarding network management and security.
