# Use an official Python runtime as a parent image
# This base image supports both amd64 and arm64 architectures
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies for building TA-Lib and git for VCS access.
# Then, download, compile, and install the TA-Lib C library from source.
# Finally, clean up to keep the image size small.
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential wget git && \
    wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib ta-lib-0.4.0-src.tar.gz && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir ensures the image is smaller
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container
COPY . .

# Since this project is a collection of scripts and strategies,
# we don't set a default CMD. You can specify the command to run
# when you start a container, for example:
# docker run -it <your-image-name> python strategys/strategy_standx/standx_mm.py
