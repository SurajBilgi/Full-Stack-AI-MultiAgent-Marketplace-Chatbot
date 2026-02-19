#!/bin/bash

# Startup script for AI Agent Marketplace Chatbot
# This script checks prerequisites and starts the application

set -e

echo "🤖 AI Agent Marketplace Chatbot - Startup Script"
echo "================================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop first."
    echo "   Download from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Docker is installed and running"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env and add your OPENAI_API_KEY"
    echo "   Then run this script again."
    exit 1
fi

# Check if OPENAI_API_KEY is set
if ! grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
    echo "⚠️  OPENAI_API_KEY not configured in .env file"
    echo "📝 Please add your OpenAI API key to .env:"
    echo "   OPENAI_API_KEY=sk-your-key-here"
    echo ""
    echo "Or run without OpenAI (limited functionality):"
    echo "   OPENAI_API_KEY=none docker compose up --build"
    exit 1
fi

echo "✅ Environment configured"
echo ""

# Check if ports are available
echo "🔍 Checking port availability..."

check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo "❌ Port $1 is already in use"
        echo "   Process: $(lsof -Pi :$1 -sTCP:LISTEN | grep LISTEN)"
        return 1
    else
        echo "✅ Port $1 is available"
        return 0
    fi
}

PORTS_OK=true
check_port 3000 || PORTS_OK=false
check_port 7474 || PORTS_OK=false
check_port 7687 || PORTS_OK=false
check_port 8000 || PORTS_OK=false

if [ "$PORTS_OK" = false ]; then
    echo ""
    echo "❌ Some required ports are in use. Please stop those services first."
    exit 1
fi

echo ""
echo "🚀 Starting application..."
echo ""
echo "This will:"
echo "  1. Build Docker images"
echo "  2. Start Neo4j database"
echo "  3. Initialize backend with seed data"
echo "  4. Start FastAPI server"
echo "  5. Start Next.js frontend"
echo ""
echo "First startup may take 5-10 minutes..."
echo ""

# Start docker compose
docker compose up --build

# Note: Script will stay running to show logs
# Press Ctrl+C to stop all services
