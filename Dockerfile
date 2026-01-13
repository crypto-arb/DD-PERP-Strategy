# Use the full Debian "Bullseye" image which has ta-lib-dev in its repositories.
# This is simpler and faster than compiling from source, though the image is larger.
FROM python:3.11-bullseye

# Set the working directory in the container
WORKDIR /app

# Install ta-lib-dev from apt, which is the method described in the README.
# The package for building against is typically 'ta-lib-dev'.
# Also install git for any potential VCS dependencies.
RUN apt-get update && \
    apt-get install -y --no-install-recommends ta-lib-dev git && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container
COPY . .

# Since this project is a collection of scripts and strategies,
# we don't set a default CMD. You can specify the command to run
# when you start a container.