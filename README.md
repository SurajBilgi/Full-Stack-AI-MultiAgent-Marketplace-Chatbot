# 🤖 AI Agent Marketplace Chatbot

A production-grade AI-powered chatbot for electronics e-commerce, featuring RAG, graph database integration, and intelligent tool calling.

## 🏗️ Architecture

### Tech Stack
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python 3.11
- **LLM**: OpenAI GPT-4 (configurable)
- **RAG**: FAISS + Sentence Transformers
- **Graph DB**: Neo4j
- **Orchestration**: Docker + Docker Compose

### Key Features
✅ Natural language chat interface  
✅ Product information retrieval via RAG  
✅ Product comparison via graph database  
✅ Order status tracking  
✅ Complaint submission & tracking  
✅ Refund status checking  
✅ Delivery tracking  
✅ Conversation memory  
✅ Intent classification  
✅ Tool calling orchestration  

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI API Key (or use local LLM)

### Setup

1. **Clone and navigate to project**
```bash
cd /Users/surajbilgi/Documents/MyWork/Full-Stack-AI-Agent-Marketplace-Chatbot
```

2. **Set environment variables**
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

3. **Start the application**
```bash
docker compose up --build
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474 (user: neo4j, pass: password123)

### Manual Setup (Development)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m app.db.seed_data  # Initialize data
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 📁 Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application
│   │   ├── agents/
│   │   │   ├── orchestrator.py     # Main AI agent
│   │   │   └── intent_classifier.py
│   │   ├── rag/
│   │   │   ├── pipeline.py         # RAG implementation
│   │   │   ├── embeddings.py
│   │   │   └── vector_store.py
│   │   ├── tools/
│   │   │   ├── order_tool.py
│   │   │   ├── complaint_tool.py
│   │   │   ├── refund_tool.py
│   │   │   └── delivery_tool.py
│   │   ├── db/
│   │   │   ├── graph_db.py         # Neo4j integration
│   │   │   ├── data_store.py       # In-memory store
│   │   │   └── seed_data.py
│   │   ├── schemas/
│   │   │   └── models.py
│   │   └── services/
│   │       └── llm_service.py
│   ├── data/
│   │   ├── products.json
│   │   ├── orders.json
│   │   ├── documents/              # RAG documents
│   │   └── ...
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx            # Main chat page
│   │   │   └── layout.tsx
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── ProductBrowser.tsx
│   │   │   ├── OrderLookup.tsx
│   │   │   └── ComplaintForm.tsx
│   │   └── lib/
│   │       └── api.ts
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🔧 API Endpoints

### Chat
```bash
POST /api/chat
{
  "message": "What's the best laptop under $1500?",
  "session_id": "user-123"
}
```

### Products
```bash
GET /api/products
GET /api/products/{product_id}
GET /api/products/compare?ids=1,2,3
```

### Orders
```bash
GET /api/orders/{order_id}
POST /api/complaints
GET /api/refunds/{order_id}
GET /api/delivery/{order_id}
```

## 💬 Example Conversations

### Product Information
**User**: "Tell me about the TechPro X1 laptop"  
**Agent**: *Uses RAG to retrieve product manual and specs*  
"The TechPro X1 is a high-performance laptop featuring an Intel i7 processor, 16GB RAM, and 512GB SSD..."

### Product Comparison
**User**: "Compare the X1 and X2 laptops"  
**Agent**: *Queries graph database for product relationships*  
"Here's a detailed comparison: The X1 has better battery life (12hrs vs 8hrs), while the X2 offers more storage..."

### Order Tracking
**User**: "What's the status of order ORD-1001?"  
**Agent**: *Calls order_tool*  
"Your order ORD-1001 is currently in transit and expected to arrive on Feb 12, 2026."

### Refund Request
**User**: "I want to return my order ORD-1002"  
**Agent**: *Calls refund_tool*  
"I can help you with that. Your order is eligible for return. The refund process takes 5-7 business days..."

### Complaint Submission
**User**: "My product arrived damaged"  
**Agent**: *Calls complaint_tool*  
"I'm sorry to hear that. I've created complaint #CMP-101. Our support team will contact you within 24 hours..."

## 🧪 Testing the API

### Chat Endpoint
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What laptops do you have?",
    "session_id": "test-user"
  }'
```

### Order Status
```bash
curl http://localhost:8000/api/orders/ORD-1001
```

### Product Comparison
```bash
curl http://localhost:8000/api/products/compare?ids=1,2
```

### Create Complaint
```bash
curl -X POST http://localhost:8000/api/complaints \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "ORD-1001",
    "issue": "Product not working",
    "description": "The device won't turn on"
  }'
```

## 🎯 Agent Capabilities

The AI agent can handle:
- ✅ Product inquiries and recommendations
- ✅ Technical specifications lookup
- ✅ Product comparisons using graph relationships
- ✅ Order status tracking
- ✅ Delivery updates
- ✅ Refund processing
- ✅ Complaint submission
- ✅ Warranty information
- ✅ Accessory compatibility
- ✅ Troubleshooting assistance

## 🔍 How It Works

### 1. Intent Classification
The agent first classifies user intent:
- `product_info`: Questions about products
- `order_status`: Order tracking queries
- `complaint`: Issue reporting
- `refund`: Return/refund requests
- `delivery`: Shipping information
- `comparison`: Product comparisons
- `general`: General questions

### 2. Tool Routing
Based on intent, the agent routes to appropriate tools:
- RAG pipeline for product knowledge
- Graph DB for product relationships
- Order tool for order status
- Complaint tool for issue tracking
- Refund tool for returns
- Delivery tool for shipping updates

### 3. Context Enrichment
- RAG retrieves relevant documents
- Graph DB provides relational context
- Tools fetch real-time operational data

### 4. Response Generation
LLM synthesizes information into natural, helpful responses

## 📊 Observability

### Logging
All requests and agent decisions are logged:
```bash
docker compose logs -f backend
```

### Metrics
View API metrics at: http://localhost:8000/metrics

### Neo4j Queries
Monitor graph queries in Neo4j Browser: http://localhost:7474

## 🛠️ Configuration

### Environment Variables
```bash
# .env file
OPENAI_API_KEY=your-key-here
MODEL_NAME=gpt-4
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123
```

### Using Local LLM
To use a local model (Llama/Mistral):
1. Update `backend/app/services/llm_service.py`
2. Configure Ollama or vLLM endpoint
3. Update MODEL_NAME in .env

## 🚢 Deployment

### Production Deployment
```bash
docker compose -f docker-compose.prod.yml up -d
```

### Environment-Specific Configs
- Development: `docker-compose.yml`
- Production: `docker-compose.prod.yml`

## 📝 License

MIT License

## 🤝 Contributing

This is a demonstration project showcasing production-grade AI agent architecture.

---

**Built with ❤️ using FastAPI, Next.js, LangChain, and Neo4j**
