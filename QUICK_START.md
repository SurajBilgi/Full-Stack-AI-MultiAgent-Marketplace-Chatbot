# 🚀 Quick Start Guide - Step by Step

Complete setup guide from scratch to running application.

---

## Prerequisites Check

Before starting, verify you have:
- ✅ Python 3.11+ installed: `python3 --version`
- ✅ Node.js 18+ installed: `node --version`
- ✅ Docker Desktop installed (optional but recommended)
- ✅ OpenAI API key (get from https://platform.openai.com/api-keys)

---

## Option 1: Docker Setup (⭐ EASIEST - RECOMMENDED)

### Step 1: Configure Environment

```bash
# Navigate to project directory
cd /Users/surajbilgi/Documents/MyWork/Full-Stack-AI-Agent-Marketplace-Chatbot

# Create .env file
cp .env.example .env
```

### Step 2: Edit .env File

Open `.env` in any text editor and add your OpenAI API key:

```bash
OPENAI_API_KEY=sk-your-actual-key-here
MODEL_NAME=gpt-4
```

### Step 3: Start Everything with Docker

```bash
# Make sure Docker Desktop is running!

# Start all services (backend, frontend, Neo4j)
docker compose up --build
```

**Wait 2-3 minutes for everything to start...**

### Step 4: Access the Application

Open your browser:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474 (username: neo4j, password: password123)

### Step 5: Test the Chat

Go to http://localhost:3000 and try:
- "What laptops do you have?"
- "Track order ORD-1002"
- "Compare products 1 and 2"

**✅ Done! Everything is running.**

To stop:
```bash
# Press Ctrl+C in terminal, then:
docker compose down
```

---

## Option 2: Manual Setup (For Development)

### Part A: Backend Setup

#### Step 1: Open Terminal and Navigate to Backend

```bash
cd /Users/surajbilgi/Documents/MyWork/Full-Stack-AI-Agent-Marketplace-Chatbot/backend
```

#### Step 2: Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate it (MAC/LINUX)
source venv/bin/activate

# You should see (venv) in your terminal prompt now
```

#### Step 3: Upgrade pip

```bash
pip install --upgrade pip
```

#### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

**This will take 2-3 minutes. You'll see packages being installed...**

#### Step 5: Set Environment Variables

```bash
# Go back to project root
cd ..

# Create .env file
cp .env.example .env

# Open .env in a text editor and add:
# OPENAI_API_KEY=sk-your-key-here
```

#### Step 6: Start Neo4j (Separate Terminal)

**Open a NEW terminal window:**

```bash
# Option A: Using Docker
docker run --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  neo4j:5.16.0

# Option B: If you have Neo4j Desktop, just start it
# Make sure it's running on bolt://localhost:7687
```

#### Step 7: Seed Data

**Back in the original terminal (with venv activated):**

```bash
cd backend

# Make sure venv is activated (you should see (venv) in prompt)
# If not, run: source venv/bin/activate

# Seed the data
python -m app.db.seed_data
```

**You should see:**
```
📦 Step 1: Initializing data store...
✅ Data store initialized successfully
   - Products: 20
   - Orders: 10
   - Complaints: 5
   - Refunds: 5
🕸️  Step 2: Initializing graph database...
✅ Graph database initialized successfully
📚 Step 3: Initializing RAG pipeline...
✅ RAG pipeline initialized successfully
```

#### Step 8: Start Backend Server

```bash
# Still in backend directory with venv activated
uvicorn app.main:app --reload --port 8000
```

**You should see:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**✅ Backend is running! Keep this terminal open.**

Test it: Open browser to http://localhost:8000/health

---

### Part B: Frontend Setup

#### Step 1: Open NEW Terminal

Open a fresh terminal window (don't close the backend one!)

```bash
cd /Users/surajbilgi/Documents/MyWork/Full-Stack-AI-Agent-Marketplace-Chatbot/frontend
```

#### Step 2: Install Node Dependencies

```bash
npm install
```

**This will take 2-3 minutes...**

#### Step 3: Start Frontend Development Server

```bash
npm run dev
```

**You should see:**
```
- Local:        http://localhost:3000
- ready started server on 0.0.0.0:3000
```

**✅ Frontend is running! Keep this terminal open too.**

#### Step 4: Access the Application

Open browser to: **http://localhost:3000**

You should see the TechPro AI Assistant interface!

---

## Testing the Application

### Test 1: Chat Interface

Go to http://localhost:3000 and try these queries:

1. **Product Info**: "What laptops do you have?"
2. **Product Details**: "Tell me about the TechPro X1 laptop"
3. **Comparison**: "Compare products 1 and 2"
4. **Order Tracking**: "Track order ORD-1002"
5. **Policy Question**: "What's your return policy?"

### Test 2: API Endpoints

Open a new terminal and test the API:

```bash
# Health check
curl http://localhost:8000/health

# Chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What laptops do you have?",
    "session_id": "test-123"
  }'

# Get products
curl http://localhost:8000/api/products

# Get order
curl http://localhost:8000/api/orders/ORD-1001
```

### Test 3: API Documentation

Visit: http://localhost:8000/docs

You'll see interactive Swagger documentation where you can test all endpoints.

### Test 4: Neo4j Browser

Visit: http://localhost:7474

Login:
- Username: `neo4j`
- Password: `password123`

Try this Cypher query:
```cypher
MATCH (p:Product)
RETURN p
LIMIT 10
```

---

## Common Issues & Solutions

### Issue 1: "ModuleNotFoundError"

**Problem**: Python packages not installed

**Solution**:
```bash
cd backend
source venv/bin/activate  # Make sure venv is active!
pip install -r requirements.txt
```

### Issue 2: "Port already in use"

**Problem**: Port 8000 or 3000 is busy

**Solution**:
```bash
# Check what's using the port
lsof -i :8000  # or :3000

# Kill it
kill -9 <PID>

# Or use different port
uvicorn app.main:app --reload --port 8001
```

### Issue 3: "Neo4j connection failed"

**Problem**: Neo4j not running

**Solution**:
```bash
# Start Neo4j with Docker
docker run --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  neo4j:5.16.0
```

### Issue 4: "OPENAI_API_KEY not set"

**Problem**: Environment variable missing

**Solution**:
```bash
# Edit .env file in project root
nano .env

# Add this line:
OPENAI_API_KEY=sk-your-actual-key-here

# Save and restart backend
```

### Issue 5: Frontend can't connect to backend

**Problem**: CORS or backend not running

**Solution**:
1. Make sure backend is running on port 8000
2. Check http://localhost:8000/health works
3. Restart frontend: `npm run dev`

### Issue 6: "No data found" in chat

**Problem**: Data not seeded

**Solution**:
```bash
cd backend
source venv/bin/activate
python -m app.db.seed_data
```

---

## Quick Reference Commands

### Starting the Application (Manual)

**Terminal 1 - Neo4j:**
```bash
docker run --name neo4j -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 neo4j:5.16.0
```

**Terminal 2 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

### Starting with Docker (Easy)

**Single Terminal:**
```bash
docker compose up --build
```

### Stopping Everything

**Manual:**
- Press Ctrl+C in each terminal

**Docker:**
```bash
docker compose down
```

---

## Development Workflow

### Daily Development

1. **Start Backend:**
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload --port 8000
   ```

2. **Start Frontend (new terminal):**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Make changes to code** - servers auto-reload!

4. **Test changes** at http://localhost:3000

### Adding New Data

To reset/update data:
```bash
cd backend
source venv/bin/activate
python -m app.db.seed_data
```

### Checking Logs

**Backend logs**: Check terminal running uvicorn

**Frontend logs**: Check terminal running npm

**Docker logs**:
```bash
docker compose logs -f backend
docker compose logs -f frontend
```

---

## Next Steps

After setup, explore:

1. **README.md** - Project overview
2. **ARCHITECTURE.md** - Technical deep dive
3. **EXAMPLES.md** - Sample conversations
4. **INTERVIEW.md** - Interview preparation
5. **API Docs** - http://localhost:8000/docs

---

## Getting Help

If you're stuck:

1. Check terminal for error messages
2. Verify all services are running
3. Check logs: `docker compose logs -f`
4. Review this guide's "Common Issues" section
5. Make sure you activated venv: `source venv/bin/activate`

---

## Summary Checklist

- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] Docker running (if using Docker)
- [ ] .env file created with OPENAI_API_KEY
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Neo4j running
- [ ] Data seeded
- [ ] Backend server running (port 8000)
- [ ] Frontend server running (port 3000)
- [ ] Can access http://localhost:3000
- [ ] Can chat with the bot

**🎉 You're all set! Happy coding!**
