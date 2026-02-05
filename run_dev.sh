#!/bin/bash

# Start Backend
echo "Starting Backend..."
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
# Bind to specific IP for external access
uvicorn deep_reader.server.app:app --host 10.102.136.54 --port 8000 --reload &
BACKEND_PID=$!

# Start Frontend
echo "Starting Frontend..."
cd web
# Bind to specific IP using -H
npm run dev -- -p 3001 -H 10.102.136.54 &
FRONTEND_PID=$!

# Handle shutdown
trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM

wait