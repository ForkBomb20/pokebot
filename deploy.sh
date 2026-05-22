#!/bin/bash
# Deploy PokeBot to EC2
# Usage: ./deploy.sh

set -e

# Configuration — update these after instance is created
EC2_HOST=""  # e.g. ec2-xx-xx-xx-xx.compute-1.amazonaws.com
EC2_USER="ec2-user"
KEY_PATH="$HOME/.ssh/pokebot-key.pem"
REMOTE_DIR="/home/ec2-user/pokebot"

if [ -z "$EC2_HOST" ]; then
    echo "Error: Set EC2_HOST in this script first"
    exit 1
fi

SSH_CMD="ssh -i $KEY_PATH -o StrictHostKeyChecking=no $EC2_USER@$EC2_HOST"

echo "==> Pushing latest to GitHub..."
git push origin main

echo "==> Deploying to $EC2_HOST..."
$SSH_CMD << 'REMOTE'
cd ~/pokebot
git pull origin main
source env/bin/activate
pip install -r requirements.txt --quiet
sudo systemctl restart pokebot
echo "==> Bot restarted. Checking status..."
sleep 2
sudo systemctl status pokebot --no-pager | head -15
REMOTE

echo "==> Deploy complete!"
