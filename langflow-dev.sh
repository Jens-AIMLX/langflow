#!/bin/bash

# Langflow Development Script for Unix-based systems
# This script provides an all-in-one solution for Langflow development
# Author: Jens-AIMLX

# Set text colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "\n${BLUE}==================================================="
echo "    LANGFLOW DEVELOPMENT ENVIRONMENT - UNIX"
echo -e "===================================================${NC}\n"

# Check for required tools
echo "Checking for required tools..."
command -v uv >/dev/null 2>&1 || { echo -e "${RED}[ERROR] uv is not installed.${NC}"; echo "Please install uv: https://docs.astral.sh/uv/getting-started/installation/"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo -e "${RED}[ERROR] npm is not installed.${NC}"; echo "Please install Node.js: https://nodejs.org/en/download/package-manager"; exit 1; }
command -v git >/dev/null 2>&1 || { echo -e "${RED}[ERROR] git is not installed.${NC}"; echo "Please install Git: https://git-scm.com/downloads"; exit 1; }
echo -e "${GREEN}[OK] All required tools are installed.${NC}\n"

# Default values
INIT_ONLY=false
DEV_MODE=false
CLEAN=false
HELP=false
PORT=7860
HOST="0.0.0.0"
ENV_FILE=".env"
WORKERS=1

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --init-only)
      INIT_ONLY=true
      shift
      ;;
    --dev)
      DEV_MODE=true
      shift
      ;;
    --clean)
      CLEAN=true
      shift
      ;;
    --help)
      HELP=true
      shift
      ;;
    --port)
      PORT="$2"
      shift 2
      ;;
    --host)
      HOST="$2"
      shift 2
      ;;
    --env-file)
      ENV_FILE="$2"
      shift 2
      ;;
    --workers)
      WORKERS="$2"
      shift 2
      ;;
    *)
      echo -e "${YELLOW}[WARNING] Unknown argument: $1${NC}"
      shift
      ;;
  esac
done

# Display help if requested
if [ "$HELP" = true ]; then
    echo "Usage: ./langflow-dev.sh [options]"
    echo ""
    echo "Options:"
    echo "  --init-only       Initialize the environment without starting servers"
    echo "  --dev             Start in development mode with hot-reloading"
    echo "  --clean           Clean caches before initializing"
    echo "  --port PORT       Set the backend port (default: 7860)"
    echo "  --host HOST       Set the backend host (default: 0.0.0.0)"
    echo "  --env-file FILE   Specify the environment file (default: .env)"
    echo "  --workers NUM     Number of backend workers (default: 1)"
    echo "  --help            Display this help message"
    echo ""
    exit 0
fi

# Function to clear directories
clear_dirs() {
    for dir in "$@"; do
        mkdir -p "$dir" && find "$dir" -mindepth 1 -delete
    done
}

# Clean caches if requested
if [ "$CLEAN" = true ]; then
    echo "Cleaning Python cache..."
    find . -type d -name '__pycache__' -exec rm -r {} +
    find . -type f -name '*.py[cod]' -exec rm -f {} +
    find . -type f -name '*~' -exec rm -f {} +
    find . -type f -name '.*~' -exec rm -f {} +
    clear_dirs .mypy_cache
    echo -e "${GREEN}[OK] Python cache cleaned.${NC}"
    
    echo "Cleaning npm cache..."
    cd src/frontend && npm cache clean --force
    clear_dirs src/frontend/node_modules src/frontend/build src/backend/base/langflow/frontend
    rm -f src/frontend/package-lock.json
    cd ../..
    echo -e "${GREEN}[OK] NPM cache and frontend directories cleaned.${NC}\n"
fi

# Create .env file if it doesn't exist
if [ ! -f "$ENV_FILE" ]; then
  echo "Creating $ENV_FILE file..."
  touch "$ENV_FILE"
  echo -e "${GREEN}[OK] Created $ENV_FILE file.${NC}\n"
fi

# Initialize the environment
echo -e "${BLUE}==================================================="
echo "    INITIALIZING LANGFLOW DEVELOPMENT ENVIRONMENT"
echo -e "===================================================${NC}\n"

echo "Installing backend dependencies..."
uv sync --frozen --extra "postgresql"
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Failed to install backend dependencies.${NC}"
    exit 1
fi
echo -e "${GREEN}[OK] Backend dependencies installed.${NC}\n"

echo "Installing frontend dependencies..."
cd src/frontend
npm install > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Failed to install frontend dependencies.${NC}"
    cd ../..
    exit 1
fi
cd ../..
echo -e "${GREEN}[OK] Frontend dependencies installed.${NC}\n"

echo "Building frontend static files..."
cd src/frontend
CI='' npm run build 2>&1
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Failed to build frontend.${NC}"
    cd ../..
    exit 1
fi
cd ../..
echo -e "${GREEN}[OK] Frontend built successfully.${NC}\n"

# Clear destination directory
echo "Clearing destination directory..."
clear_dirs src/backend/base/langflow/frontend
echo -e "${GREEN}[OK] Destination directory cleared.${NC}\n"

# Copy build files
echo "Copying build files to backend..."
cp -r src/frontend/build/. src/backend/base/langflow/frontend
echo -e "${GREEN}[OK] Frontend files copied to backend.${NC}\n"

echo -e "${BLUE}==================================================="
echo "    INITIALIZATION COMPLETE"
echo -e "===================================================${NC}\n"

# Exit if init-only mode
if [ "$INIT_ONLY" = true ]; then
    echo "Initialization completed successfully."
    echo "Run './langflow-dev.sh --dev' to start development servers."
    exit 0
fi

# Function to handle process termination
cleanup() {
    echo -e "\n${YELLOW}Stopping all Langflow processes...${NC}"
    pkill -f "uvicorn --factory langflow.main:create_app" || true
    pkill -f "npm start" || true
    exit 0
}

# Set up trap for clean exit
trap cleanup SIGINT SIGTERM

# Start development servers if in dev mode
if [ "$DEV_MODE" = true ]; then
    echo -e "${BLUE}==================================================="
    echo "    STARTING DEVELOPMENT SERVERS"
    echo -e "===================================================${NC}\n"
    echo "Starting backend and frontend servers in development mode..."
    echo ""
    echo "Backend will be available at: http://$HOST:$PORT"
    echo "Frontend will be available at: http://localhost:3100"
    echo ""
    echo "Press Ctrl+C to stop all servers."
    echo ""
    
    # Start backend in a new terminal
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash -c "echo 'Starting Langflow Backend...'; uv run uvicorn --factory langflow.main:create_app --host $HOST --port $PORT --reload --env-file $ENV_FILE --loop asyncio --workers $WORKERS; read -p 'Press Enter to close...'"
    elif command -v xterm &> /dev/null; then
        xterm -T "Langflow Backend" -e "echo 'Starting Langflow Backend...'; uv run uvicorn --factory langflow.main:create_app --host $HOST --port $PORT --reload --env-file $ENV_FILE --loop asyncio --workers $WORKERS; read -p 'Press Enter to close...'" &
    elif command -v osascript &> /dev/null; then
        # macOS
        osascript -e "tell application \"Terminal\" to do script \"cd $(pwd) && echo 'Starting Langflow Backend...' && uv run uvicorn --factory langflow.main:create_app --host $HOST --port $PORT --reload --env-file $ENV_FILE --loop asyncio --workers $WORKERS\""
    else
        # Fallback to background process
        echo "Starting backend in background..."
        uv run uvicorn --factory langflow.main:create_app --host $HOST --port $PORT --reload --env-file $ENV_FILE --loop asyncio --workers $WORKERS &
        BACKEND_PID=$!
    fi
    
    # Start frontend in a new terminal
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash -c "cd src/frontend && echo 'Starting Langflow Frontend...'; npm start; read -p 'Press Enter to close...'"
    elif command -v xterm &> /dev/null; then
        xterm -T "Langflow Frontend" -e "cd src/frontend && echo 'Starting Langflow Frontend...'; npm start; read -p 'Press Enter to close...'" &
    elif command -v osascript &> /dev/null; then
        # macOS
        osascript -e "tell application \"Terminal\" to do script \"cd $(pwd)/src/frontend && echo 'Starting Langflow Frontend...' && npm start\""
    else
        # Fallback to background process
        echo "Starting frontend in background..."
        cd src/frontend && npm start &
        FRONTEND_PID=$!
        cd ../..
    fi
    
    echo -e "${GREEN}[OK] Development servers started.${NC}\n"
    
    # Wait for servers to start
    echo "Waiting for servers to start..."
    sleep 5
    
    # Open browser
    echo "Opening browser..."
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:3100
    elif command -v open &> /dev/null; then
        open http://localhost:3100
    else
        echo "Please open http://localhost:3100 in your browser."
    fi
    
    echo -e "${BLUE}==================================================="
    echo "    DEVELOPMENT ENVIRONMENT RUNNING"
    echo -e "===================================================${NC}\n"
    echo "Backend: http://$HOST:$PORT"
    echo "Frontend: http://localhost:3100"
    echo ""
    echo "Press Ctrl+C to stop all servers."
    echo ""
    
    # Keep script running to allow for Ctrl+C to work
    while true; do
        sleep 1
    done
    
else
    # Start the application in normal mode
    echo -e "${BLUE}==================================================="
    echo "    STARTING LANGFLOW APPLICATION"
    echo -e "===================================================${NC}\n"
    echo "Starting Langflow application..."
    echo ""
    echo "Langflow will be available at: http://$HOST:$PORT"
    echo ""
    echo "Press Ctrl+C to stop the server."
    echo ""
    
    uv run langflow run --frontend-path src/backend/base/langflow/frontend --log-level debug --host $HOST --port $PORT --env-file $ENV_FILE
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR] Failed to start Langflow application.${NC}"
        exit 1
    fi
fi
