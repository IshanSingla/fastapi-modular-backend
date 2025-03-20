#!/bin/sh

# Check if .venv exists, create it if it doesn't
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment .venv"
  python3 -m venv .venv
fi

# Activate the virtual environment
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
