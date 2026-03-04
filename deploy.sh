#!/bin/bash
# deploy.sh - Deploy HEUM-tec to Raspberry Pi

PI_IP="192.168.2.229"
PI_USER="bot"
TARGET_DIR="/home/bot/robot"

echo "Deploying HEUM-tec to $PI_USER@$PI_IP:$TARGET_DIR..."

# Create target directory on Pi
ssh $PI_USER@$PI_IP "mkdir -p $TARGET_DIR"

# Transfer files using rsync (excluding git and venv)
rsync -avz --exclude='.git/' --exclude='.venv/' --exclude='__pycache__/' ./ $PI_USER@$PI_IP:$TARGET_DIR/

# Run remote setup
ssh $PI_USER@$PI_IP "bash $TARGET_DIR/remote_setup.sh"

echo "Deployment finished."
