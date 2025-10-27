#!/bin/bash
# SSH Tunnel to Remote Ollama Server
# This script creates an SSH tunnel to access Ollama running on a remote server

# IMPORTANT: Configure these variables with your remote server details
# DO NOT commit this file with real credentials to git
REMOTE_USER="${OLLAMA_REMOTE_USER:-your_username}"
REMOTE_HOST="${OLLAMA_REMOTE_HOST:-your_server_ip}"
REMOTE_PORT="${OLLAMA_REMOTE_PORT:-11434}"
LOCAL_PORT="${OLLAMA_LOCAL_PORT:-11434}"

# Validate configuration
if [ "$REMOTE_USER" = "your_username" ] || [ "$REMOTE_HOST" = "your_server_ip" ]; then
    echo "ERROR: Please configure REMOTE_USER and REMOTE_HOST"
    echo ""
    echo "Set environment variables:"
    echo "  export OLLAMA_REMOTE_USER=your_username"
    echo "  export OLLAMA_REMOTE_HOST=192.168.1.100"
    echo ""
    echo "Or edit this script and replace the default values"
    exit 1
fi

echo "Creating SSH tunnel to Ollama server..."
echo "Remote: ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PORT}"
echo "Local: localhost:${LOCAL_PORT}"
echo ""
echo "Keep this terminal open while using the service."
echo "Press Ctrl+C to close the tunnel."
echo ""

# Create SSH tunnel
# -L: Local port forwarding
# -N: Don't execute remote command
# -v: Verbose (optional, remove for less output)
ssh -L ${LOCAL_PORT}:localhost:${REMOTE_PORT} -N ${REMOTE_USER}@${REMOTE_HOST}
