# VIT Counseling Assistant API

AI-powered VIT admission counseling assistant with vector search capabilities using FastAPI, Firebase Firestore, and Google Gemini AI.

## Features

- **FastAPI REST API** with automatic OpenAPI documentation
- **Gemini AI Integration** for intent classification and natural language responses
- **Vector Search** using Sentence Transformers (local, no API costs)
- **Firebase Firestore** for data persistence
- **Rank-based Branch Prediction** with confidence scores
- **Query Logging** for analytics
- **CORS enabled** for cross-origin requests

## Project Structure

```
.
├── main.py                    # FastAPI application entry point
├── models/
│   └── schemas.py             # Pydantic models for request/response validation
├── services/
│   ├── firebase_service.py    # Firebase Firestore operations
│   └── ai_service.py          # Gemini AI integration
├── utils/
│   ├── embeddings.py          # Sentence Transformer embeddings
│   ├── similarity.py          # Cosine similarity calculation
│   └── text_processing.py     # Text extraction utilities
├── scripts/
│   └── seed_database.py       # Database seeding script
└── requirements.txt           # Python dependencies
```

## Setup Instructions

### 1. Install Dependencies

Dependencies are already installed in this Replit environment.

### 2. Configure Secrets

You'll need to provide:
- `GEMINI_API_KEY` - Your Google Gemini API key

### 3. Upload Firebase Credentials

Upload your `firebase-credentials.json` file to the root directory of this project.

### 4. Seed the Database (Optional)

Run the seeding script to add sample FAQs and cutoff data:

```bash
python scripts/seed_database.py
```

### 5. Start the API Server

The server runs automatically on port 5000.

## API Endpoints

### Health Check
```
GET /health
```

Returns service status and availability of Firebase and AI services.

### Query Endpoint
```
POST /api/query
```

**Request Body:**
```json
{
  "query": "I got rank 15000, which branches can I get?",
  "user_id": "user123"
}
```

**Response:**
```json
{
  "answer": "Based on your rank...",
  "intent": "rank_prediction",
  "confidence": 0.95,
  "rank_prediction": {
    "rank": 15000,
    "predictions": [...]
  },
  "timestamp": "2025-11-02T12:00:00",
  "processing_time_ms": 1234.56
}
```

## Supported Query Types

1. **Rank Prediction** - "I got rank 15000, which branches can I get?"
2. **Cutoff Queries** - "What is the cutoff for CSE at Vellore?"
3. **General FAQs** - "How are the hostel facilities?", "What is FFCS?"

## Environment Variables

- `GEMINI_API_KEY` - Google Gemini API key
- `FIREBASE_CREDENTIALS_PATH` - Path to Firebase credentials JSON (default: `firebase-credentials.json`)
- `EMBEDDING_MODEL_NAME` - Sentence Transformer model (default: `all-MiniLM-L6-v2`)
- `PORT` - Server port (default: `5000`)

## API Documentation

Once the server is running, visit:
- Interactive docs: `https://your-repl-url/docs`
- Alternative docs: `https://your-repl-url/redoc`

## Notes

- The embedding model runs locally and does not incur API costs
- Gemini AI is used only for intent classification and response generation
- Firebase credentials must be uploaded manually
- The app can run without Firebase (with limited functionality) for testing
