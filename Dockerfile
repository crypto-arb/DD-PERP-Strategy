# Base on the slim Python image to keep the size down
FROM python:3.11-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Install build dependencies for ta-lib, download and build it from source
# as per the official documentation, then clean up.
# Git is also installed for any potential VCS dependencies.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        wget \
        git && \
    wget https://github.com/ta-lib/ta-lib/releases/download/v0.6.4/ta-lib-0.6.4-src.tar.gz -q -O ta-lib-0.6.4-src.tar.gz && \
    tar -xzf ta-lib-0.6.4-src.tar.gz && \
    cd ta-lib-0.6.4/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib-0.6.4 ta-lib-0.6.4-src.tar.gz && \
    apt-get purge -y build-essential wget && \
    apt-get autoremove -y && \
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