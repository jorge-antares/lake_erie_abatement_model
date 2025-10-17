#! /bin/zsh

# Create environment
python3 -m venv .venv

# Install dependencies
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
