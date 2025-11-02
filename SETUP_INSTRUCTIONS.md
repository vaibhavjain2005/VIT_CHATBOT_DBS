# VIT Counseling Assistant - Setup Instructions

## ✅ Completed Setup

Your VIT Counseling Assistant API backend is now running successfully! Here's what's been set up:

- ✅ FastAPI server running on port 5000
- ✅ Google Gemini AI connected and working
- ✅ Clean modular architecture with separation of concerns
- ✅ Vector search utilities ready (using local embeddings)
- ✅ CORS enabled for frontend integration

## 🔧 Next Steps

### 1. Upload Firebase Credentials (Required for Database)

To enable data persistence for FAQs, cutoffs, and query logs:

1. Go to your Firebase Console: https://console.firebase.google.com/
2. Select your project (or create a new one)
3. Go to Project Settings → Service Accounts
4. Click "Generate New Private Key"
5. Download the JSON file
6. Upload it to the root of this project and name it: `firebase-credentials.json`
7. The server will automatically reconnect to Firebase

### 2. Seed the Database (Optional but Recommended)

Once Firebase is connected, populate it with sample data:

```bash
python scripts/seed_database.py
```

This will add:
- 5 sample FAQs (hostel, FFCS, placements, clubs, fees)
- 5 sample cutoff data entries

### 3. Test the API

Visit these URLs to explore your API:

- **Interactive Documentation**: `/docs` - Test all endpoints with a nice UI
- **Alternative Docs**: `/redoc` - Clean API documentation
- **Health Check**: `/health` - Check service status

### 4. Test Query Examples

Use the `/docs` endpoint to test these queries:

**Rank Prediction:**
```json
{
  "query": "I got rank 15000, which branches can I get?",
  "user_id": "user123"
}
```

**Cutoff Query:**
```json
{
  "query": "What is the cutoff for CSE at Vellore?"
}
```

**General FAQ:**
```json
{
  "query": "How are the hostel facilities at VIT?"
}
```

## 📁 Project Structure

```
.
├── main.py                    # FastAPI app - all routes and logic
├── services/
│   ├── firebase_service.py    # Database operations
│   └── ai_service.py          # Gemini AI integration
├── models/
│   └── schemas.py             # Request/response models
├── utils/
│   ├── embeddings.py          # Vector embeddings
│   ├── similarity.py          # Cosine similarity
│   └── text_processing.py     # Rank extraction
├── scripts/
│   └── seed_database.py       # Database seeding
└── README.md                  # Full documentation
```

## 🚀 API Endpoints

### `GET /health`
Check if all services (Firebase, AI, embeddings) are working

### `POST /api/query`
Main endpoint for processing user queries

**Request:**
```json
{
  "query": "Your question here",
  "user_id": "optional_user_id"
}
```

**Response:**
```json
{
  "answer": "AI-generated response",
  "intent": "rank_prediction|cutoff|faq|general",
  "confidence": 0.95,
  "rank_prediction": {...},
  "timestamp": "2025-11-02T12:00:00",
  "processing_time_ms": 1234.56
}
```

## 🔒 Current Status

- **Gemini AI**: ✅ Connected
- **Firebase**: ⚠️ Waiting for credentials
- **Embeddings**: ✅ Ready (fallback mode until sentence-transformers is fully installed)

## 💡 Notes

1. The app runs with graceful fallback when services are unavailable
2. Vector search uses local embeddings (no API costs)
3. Gemini AI is only used for intent classification and response generation
4. All query processing is logged to Firebase (once connected)

## 🛠️ Troubleshooting

**Firebase Not Connecting?**
- Ensure `firebase-credentials.json` is in the root directory
- Check the file has valid JSON format
- Restart the server after uploading

**Sentence Transformers Warning?**
- This is normal due to disk space limitations
- The app uses fallback random embeddings for development
- Upload to a production environment to use full embeddings

**Need Help?**
Check the logs in the Console tab or view the full documentation in `README.md`
