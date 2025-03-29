#!/bin/bash

# Install dependencies
echo "Updating system and installing dependencies..."
sudo apt update
sudo apt install -y python3-pip exiftool

# Install the project
echo "Installing the project..."
pip install .

# Confirm installation
echo "Setup complete! Run 'organize' to execute the project."
