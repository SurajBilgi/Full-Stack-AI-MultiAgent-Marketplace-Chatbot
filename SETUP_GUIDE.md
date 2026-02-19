# 🚀 Setup Guide

Complete setup instructions for the AI Agent Marketplace Chatbot.

## Prerequisites

- Docker Desktop installed and running
- OpenAI API key (or configure for local LLM)
- At least 4GB free RAM
- Ports 3000, 7474, 7687, and 8000 available

## Quick Start (Docker)

### 1. Clone and Navigate

```bash
cd /Users/surajbilgi/Documents/MyWork/Full-Stack-AI-Agent-Marketplace-Chatbot
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```bash
OPENAI_API_KEY=sk-your-key-here
```

### 3. Start Application

```bash
docker compose up --build
```

This will:
- Start Neo4j graph database
- Initialize backend with seed data
- Start FastAPI server
- Launch Next.js frontend

### 4. Access Applications

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474

Default Neo4j credentials:
- Username: `neo4j`
- Password: `password123`

### 5. Verify Everything Works

Visit http://localhost:3000 and try these queries in the chat:
- "What laptops do you have?"
- "Track order ORD-1002"
- "Compare products 1 and 2"
- "What's your return policy?"

## Manual Setup (Development)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=your-key-here
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=password123

# Seed data
python -m app.db.seed_data

# Start server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Neo4j Setup

If running manually:

```bash
docker run \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  neo4j:5.16.0
```

## Configuration Options

### Using Local LLM (Optional)

If you don't have an OpenAI API key, you can use a local model:

1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull llama2`
3. Update `backend/app/services/llm_service.py` to use Ollama
4. Remove `OPENAI_API_KEY` from `.env`

### Environment Variables

**Backend (.env)**:
```bash
# LLM Configuration
OPENAI_API_KEY=your-key-here
MODEL_NAME=gpt-4
EMBEDDING_MODEL=text-embedding-ada-002
TEMPERATURE=0.7

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123

# RAG
VECTOR_STORE_PATH=./data/vector_store
TOP_K_RESULTS=3
MAX_CONVERSATION_HISTORY=10
```

**Frontend (.env.local)**:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Troubleshooting

### Port Already in Use

If ports are busy:

```bash
# Check what's using the port
lsof -i :8000  # or :3000, :7474, :7687

# Kill the process
kill -9 <PID>
```

### Neo4j Connection Issues

```bash
# Check Neo4j logs
docker logs techpro-neo4j

# Restart Neo4j
docker restart techpro-neo4j
```

### Backend Not Starting

```bash
# Check backend logs
docker logs techpro-backend

# Common issues:
# - Missing OPENAI_API_KEY
# - Neo4j not ready
# - Port 8000 in use
```

### Frontend Build Errors

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Vector Store Issues

If RAG isn't working:

```bash
cd backend
rm -rf data/vector_store
python -m app.db.seed_data
```

## Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What laptops do you have?",
    "session_id": "test-123"
  }'

# Get products
curl http://localhost:8000/api/products

# Track order
curl http://localhost:8000/api/orders/ORD-1001

# Compare products
curl "http://localhost:8000/api/products/compare?ids=1,2"
```

### Using the API Docs

Visit http://localhost:8000/docs for interactive API documentation with Swagger UI.

## Data Seeding

The application automatically seeds data on first run. To reseed:

```bash
cd backend
python -m app.db.seed_data
```

This creates:
- 20 products (laptops, phones, TVs, accessories)
- 10 orders with various statuses
- 5 complaints
- 5 refunds
- Delivery tracking data
- Product manuals and FAQs for RAG
- Graph relationships in Neo4j

## Performance Optimization

### For Production

1. **Use GPU for embeddings** (if available)
2. **Enable caching** for frequently accessed data
3. **Use production-grade database** instead of in-memory store
4. **Configure Redis** for session management
5. **Enable CDN** for frontend assets
6. **Use Nginx** as reverse proxy

### Resource Requirements

**Minimum**:
- 4GB RAM
- 2 CPU cores
- 5GB disk space

**Recommended**:
- 8GB RAM
- 4 CPU cores
- 10GB disk space

## Next Steps

1. ✅ Verify all services are running
2. ✅ Test the chat interface
3. ✅ Browse products
4. ✅ Track an order
5. ✅ Submit a complaint
6. 📚 Read the main README for architecture details
7. 🔧 Customize for your use case

## Support

For issues or questions:
- Check logs: `docker compose logs -f`
- Review API docs: http://localhost:8000/docs
- Verify health: http://localhost:8000/health

## Cleanup

To stop and remove everything:

```bash
docker compose down -v
```

To restart fresh:

```bash
docker compose down -v
docker compose up --build
```
