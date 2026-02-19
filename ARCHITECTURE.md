# 🏗️ Architecture Documentation

Detailed technical architecture of the AI Agent Marketplace Chatbot.

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Layer                            │
│                   (Next.js Frontend)                         │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────────────────┐
│                  Application Layer                           │
│                  (FastAPI Backend)                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           Agent Orchestrator (Core Logic)              │ │
│  └─────┬──────────────┬──────────────┬──────────────┬─────┘ │
│        │              │              │              │       │
│   ┌────▼────┐   ┌────▼────┐   ┌────▼────┐   ┌────▼────┐  │
│   │   RAG   │   │  Graph  │   │  Tools  │   │   LLM   │  │
│   │ Pipeline│   │   DB    │   │ Engine  │   │ Service │  │
│   └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘  │
└────────┼─────────────┼─────────────┼─────────────┼────────┘
         │             │             │             │
    ┌────▼────┐   ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
    │  FAISS  │   │  Neo4j  │   │  Data   │   │ OpenAI  │
    │ Vector  │   │  Graph  │   │  Store  │   │   API   │
    │  Store  │   │   DB    │   │ (JSON)  │   │         │
    └─────────┘   └─────────┘   └─────────┘   └─────────┘
```

## Component Architecture

### 1. Frontend (Next.js + TypeScript + Tailwind)

**Purpose**: User interface for interacting with the AI agent.

**Components**:
- `ChatInterface.tsx`: Main chat UI with message history
- `ProductBrowser.tsx`: Product catalog with filtering
- `OrderLookup.tsx`: Order tracking interface
- `ComplaintForm.tsx`: Support ticket submission

**Features**:
- Real-time chat with loading states
- Responsive design (mobile, tablet, desktop)
- TypeScript for type safety
- Tailwind CSS for modern styling
- API client with error handling

**Data Flow**:
1. User enters message
2. Frontend sends POST to `/api/chat`
3. Displays loading indicator
4. Receives and renders response
5. Shows intent and sources (if available)

### 2. Backend (FastAPI + Python)

**Purpose**: Business logic, AI orchestration, data management.

**Structure**:
```
backend/
├── app/
│   ├── main.py              # FastAPI app, routes, lifecycle
│   ├── agents/              # AI agent logic
│   │   ├── orchestrator.py  # Main agent coordinator
│   │   └── intent_classifier.py  # Intent detection
│   ├── rag/                 # Retrieval-Augmented Generation
│   │   ├── pipeline.py      # RAG orchestration
│   │   ├── embeddings.py    # Text → Vector conversion
│   │   └── vector_store.py  # FAISS operations
│   ├── tools/               # Tool functions
│   │   ├── order_tool.py
│   │   ├── complaint_tool.py
│   │   ├── refund_tool.py
│   │   └── delivery_tool.py
│   ├── db/                  # Data layer
│   │   ├── graph_db.py      # Neo4j integration
│   │   ├── data_store.py    # In-memory data
│   │   └── seed_data.py     # Data initialization
│   ├── services/            # External services
│   │   └── llm_service.py   # OpenAI/LLM wrapper
│   └── schemas/             # Pydantic models
│       └── models.py
└── data/                    # Data files
    ├── products.json
    ├── orders.json
    ├── complaints.json
    ├── refunds.json
    ├── deliveries.json
    └── documents/           # RAG documents
        ├── product_manuals.json
        ├── faqs.json
        └── policies.json
```

### 3. AI Agent Orchestrator

**Purpose**: Brain of the system - routes queries to appropriate handlers.

**Workflow**:

```python
async def process_message(message, session_id):
    # 1. Classify Intent
    intent = classify_intent(message)
    # → "product_info", "order_status", "complaint", etc.
    
    # 2. Route to Handler
    if intent == "product_info":
        # Use RAG to retrieve product information
        context = await rag_pipeline.retrieve(message)
        data = {"context": context}
    elif intent == "comparison":
        # Use Graph DB for product comparison
        products = extract_product_ids(message)
        data = await graph_db.compare_products(products)
    elif intent == "order_status":
        # Use Order Tool
        order_id = extract_order_id(message)
        data = await order_tool.get_status(order_id)
    # ... other intents
    
    # 3. Generate Response
    response = await llm_service.generate_response(
        message=message,
        context=data,
        history=get_conversation_history(session_id)
    )
    
    return response
```

**Conversation Memory**:
- Stores last 10 messages per session
- Session ID from frontend
- Used for context in LLM prompts

### 4. RAG Pipeline

**Purpose**: Retrieve relevant documents to answer product questions.

**Process**:

```python
# Initialization (on startup)
1. Load documents from JSON files
2. Chunk into 500-character pieces with overlap
3. Generate embeddings (OpenAI or sentence-transformers)
4. Store in FAISS vector index
5. Save index to disk for reuse

# Query Time
1. User asks: "Tell me about the X1 laptop"
2. Generate query embedding
3. Search FAISS for top-3 similar chunks
4. Return relevant text + metadata
5. Inject into LLM prompt as context
6. LLM generates natural answer
```

**Documents**:
- **Product Manuals**: Detailed specs, setup, usage
- **FAQs**: Common questions and answers
- **Policies**: Return, warranty, shipping policies

**Embedding Models**:
- OpenAI: `text-embedding-ada-002` (1536 dims)
- Local: `all-MiniLM-L6-v2` (384 dims)

### 5. Graph Database (Neo4j)

**Purpose**: Store product relationships for intelligent comparisons.

**Schema**:

```cypher
# Nodes
(p:Product {
  id, name, category, brand, price,
  rating, warranty, description
})

(s:Spec {key, value})

# Relationships
(p)-[:HAS_SPEC]->(s)
(p1)-[:SAME_CATEGORY]->(p2)
(p1)-[:COMPATIBLE_WITH]->(p2)
```

**Queries**:

```cypher
# Compare products
MATCH (p:Product)
WHERE p.id IN [1, 2]
OPTIONAL MATCH (p)-[:HAS_SPEC]->(s:Spec)
RETURN p, collect(s) as specs

# Find compatible accessories
MATCH (p1:Product {id: 1})-[:COMPATIBLE_WITH]->(p2:Product)
RETURN p2

# Same category products
MATCH (p1:Product {id: 1})-[:SAME_CATEGORY]->(p2:Product)
RETURN p2
ORDER BY p2.rating DESC
LIMIT 5
```

### 6. Tools System

**Purpose**: Execute specific actions (orders, complaints, refunds).

**Tool Architecture**:

```python
class OrderTool:
    def __init__(self, data_store):
        self.data_store = data_store
    
    async def get_order_status(self, order_id: str):
        order = self.data_store.get_order(order_id)
        return formatted_response(order)
```

**Available Tools**:
- `OrderTool`: Track orders, list customer orders
- `ComplaintTool`: Create and track complaints
- `RefundTool`: Initiate and check refund status
- `DeliveryTool`: Get tracking information

### 7. LLM Service

**Purpose**: Interface with language models for generation and classification.

**Capabilities**:

```python
class LLMService:
    # Generate response with context
    async def generate_response(prompt, context, system_message)
    
    # Generate with conversation history
    async def generate_with_history(messages)
    
    # Classify user intent
    async def classify_intent(message)
    
    # Extract entities (order IDs, product names)
    async def extract_entities(message)
```

**Fallback Behavior**:
- If OpenAI unavailable → rule-based responses
- Intent classification → keyword matching
- Context-aware fallbacks for better UX

## Data Flow Examples

### Example 1: Product Information Query

```
User: "Tell me about the TechPro X1 laptop"
  ↓
Frontend → POST /api/chat
  ↓
Agent Orchestrator
  ├─→ Intent Classifier → "product_info"
  ├─→ RAG Pipeline
  │    ├─→ Generate query embedding
  │    ├─→ Search FAISS (top-3 chunks)
  │    └─→ Return: [product manual, specs, reviews]
  └─→ LLM Service
       ├─→ Build prompt with context
       ├─→ Generate natural response
       └─→ Return formatted answer
  ↓
Frontend displays response with sources
```

### Example 2: Order Tracking

```
User: "Track my order ORD-1002"
  ↓
Agent Orchestrator
  ├─→ Intent Classifier → "order_status"
  ├─→ Extract order ID → "ORD-1002"
  ├─→ Order Tool
  │    └─→ Data Store → get_order("ORD-1002")
  └─→ LLM Service
       └─→ Format natural response
  ↓
Response: "Your order ORD-1002 is in transit..."
```

### Example 3: Product Comparison

```
User: "Compare products 1 and 2"
  ↓
Agent Orchestrator
  ├─→ Intent Classifier → "comparison"
  ├─→ Extract IDs → [1, 2]
  ├─→ Graph Database
  │    ├─→ MATCH products with IDs
  │    ├─→ Collect specs
  │    └─→ Generate comparison matrix
  └─→ LLM Service
       └─→ Synthesize comparison into prose
  ↓
Response: "The X1 has better battery (12hrs vs 8hrs)..."
```

## Technology Stack

### Backend
- **Framework**: FastAPI 0.109
- **Language**: Python 3.11
- **LLM**: OpenAI GPT-4
- **Embeddings**: OpenAI Ada-002 / Sentence Transformers
- **Vector Store**: FAISS
- **Graph DB**: Neo4j 5.16
- **Data Validation**: Pydantic

### Frontend
- **Framework**: Next.js 14
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Icons**: Lucide React

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Web Server**: Uvicorn (ASGI)

## Scalability Considerations

### Current Design (Demo/MVP)
- In-memory data store
- Single backend instance
- Local vector store

### Production Enhancements

**1. Database**:
- Replace in-memory store with PostgreSQL
- Use Redis for session management
- Separate read/write replicas

**2. Vector Store**:
- Use Pinecone or Weaviate for distributed vectors
- Or Qdrant for self-hosted option
- Enable similarity caching

**3. API Layer**:
- Horizontal scaling with load balancer
- API gateway (Kong, Tyk)
- Rate limiting and authentication

**4. LLM**:
- Use LangChain for advanced orchestration
- Implement caching for repeated queries
- Consider fine-tuned models for domain

**5. Monitoring**:
- Prometheus + Grafana for metrics
- ELK stack for log aggregation
- Sentry for error tracking

## Security Considerations

**Current**:
- CORS configured for localhost
- No authentication (demo)
- Environment variables for secrets

**Production Additions**:
- OAuth 2.0 / JWT authentication
- API key management
- Rate limiting per user/IP
- Input sanitization
- SQL injection prevention
- XSS protection
- HTTPS/TLS encryption
- Secrets management (Vault, AWS Secrets)

## Performance Metrics

**Target Latencies**:
- Chat response: < 2 seconds
- Product search: < 500ms
- Order lookup: < 200ms
- Graph comparison: < 1 second

**Optimization Techniques**:
- Async/await throughout
- Connection pooling
- Index optimization
- Response caching
- Batch processing where possible

## Extension Points

**Adding New Intents**:
1. Add intent to `IntentClassifier`
2. Create handler in `Orchestrator`
3. Implement tool if needed
4. Update LLM system prompts

**Adding New Tools**:
1. Create tool class in `app/tools/`
2. Initialize in `Orchestrator.__init__`
3. Add routing logic
4. Test with sample queries

**Adding New Data Sources**:
1. Create data file in `data/`
2. Add loader in `DataStore` or create new store
3. Seed data in `seed_data.py`
4. Integrate into relevant tools

## Testing Strategy

**Unit Tests** (not included, recommended):
- Test each tool independently
- Mock external services (LLM, Neo4j)
- Validate data transformations

**Integration Tests**:
- Test full chat flow end-to-end
- Verify RAG retrieval accuracy
- Check graph queries return correct data

**Manual Testing**:
- Try example queries from README
- Test edge cases (invalid order IDs)
- Verify UI responsiveness

---

For implementation details, see source code with inline comments.
