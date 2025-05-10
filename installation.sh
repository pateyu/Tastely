#!/bin/bash

# Exit on any error
set -e

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
   echo "Python3 is not installed. Installing Python3..."
   sudo apt update
   sudo apt install python3 python3-pip -y
else
   echo "Python3 is already installed."
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null
then
   echo "pip3 is not installed. Installing pip3..."
   sudo apt install python3-pip -y
else
   echo "pip3 is already installed."
fi

# Install Flask and other necessary packages
echo "Installing Flask and other required packages..."
pip3 install -r requirements.txt



# Initialize the database and start the application
echo "Initializing the database and starting the application..."
python3 app.py



echo "Setup complete."

