#!/bin/bash

# WebApp Firewall Simulator - Docker Deployment Script
# Created by Van Glenndon Enad

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="webapp-firewall-simulator"
CONTAINER_NAME="firewall-sim"
PORT="5000"
DOCKER_CMD="sudo docker"

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_success "Docker is installed"
}

# Function to check if port is available
check_port() {
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port $PORT is already in use"
        read -p "Do you want to use a different port? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            read -p "Enter port number: " PORT
        else
            print_error "Cannot proceed with port $PORT already in use"
            exit 1
        fi
    fi
}

# Function to stop and remove existing container
cleanup() {
    if $DOCKER_CMD ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_info "Stopping and removing existing container..."
        $DOCKER_CMD stop $CONTAINER_NAME >/dev/null 2>&1 || true
        $DOCKER_CMD rm $CONTAINER_NAME >/dev/null 2>&1 || true
        print_success "Cleaned up existing container"
    fi
}

# Function to build Docker image
build_image() {
    print_info "Building Docker image..."
    $DOCKER_CMD build -t $IMAGE_NAME . || {
        print_error "Failed to build Docker image"
        exit 1
    }
    print_success "Docker image built successfully"
}

# Function to run container
run_container() {
    print_info "Starting container on port $PORT..."
    $DOCKER_CMD run -d -p $PORT:5000 --name $CONTAINER_NAME --restart unless-stopped $IMAGE_NAME || {
        print_error "Failed to start container"
        exit 1
    }
    print_success "Container started successfully"
}

# Function to show logs
show_logs() {
    print_info "Showing container logs (Ctrl+C to exit)..."
    sleep 2
    $DOCKER_CMD logs -f $CONTAINER_NAME
}

# Main menu
show_menu() {
    echo ""
    echo "=========================================="
    echo "  WebApp Firewall Simulator - Docker"
    echo "=========================================="
    echo "1. Build and Run"
    echo "2. Build Only"
    echo "3. Run Only"
    echo "4. Stop"
    echo "5. Restart"
    echo "6. View Logs"
    echo "7. Clean Up (remove container and image)"
    echo "8. Status"
    echo "9. Exit"
    echo "=========================================="
    read -p "Select option: " choice
}

# Handle menu selection
handle_choice() {
    case $choice in
        1)
            check_docker
            check_port
            cleanup
            build_image
            run_container
            print_success "Application is running at http://localhost:$PORT"
            read -p "Show logs? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                show_logs
            fi
            ;;
        2)
            check_docker
            build_image
            ;;
        3)
            check_docker
            check_port
            cleanup
            run_container
            print_success "Application is running at http://localhost:$PORT"
            ;;
        4)
            print_info "Stopping container..."
            $DOCKER_CMD stop $CONTAINER_NAME && print_success "Container stopped"
            ;;
        5)
            print_info "Restarting container..."
            $DOCKER_CMD restart $CONTAINER_NAME && print_success "Container restarted"
            ;;
        6)
            show_logs
            ;;
        7)
            print_info "Cleaning up..."
            $DOCKER_CMD stop $CONTAINER_NAME >/dev/null 2>&1 || true
            $DOCKER_CMD rm $CONTAINER_NAME >/dev/null 2>&1 || true
            $DOCKER_CMD rmi $IMAGE_NAME >/dev/null 2>&1 || true
            print_success "Cleanup complete"
            ;;
        8)
            echo ""
            $DOCKER_CMD ps -a --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
            echo ""
            ;;
        9)
            print_info "Exiting..."
            exit 0
            ;;
        *)
            print_error "Invalid option"
            ;;
    esac
}

# Main loop
while true; do
    show_menu
    handle_choice
    echo ""
    read -p "Press Enter to continue..."
done
