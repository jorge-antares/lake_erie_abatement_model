#! /bin/zsh

# Create environment
python3 -m venv cvxenv

# Install dependencies
source ./cvxenv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
