# VIT Counseling Assistant Backend

## Overview
Production-ready FastAPI backend for a VIT/VITEEE admission counseling chatbot. The system uses AI-powered intent classification, vector search for semantic matching, and rank-based branch prediction.

## Recent Changes
- **2025-11-02**: Initial backend setup with clean separation of concerns
  - Created modular architecture with services/, models/, utils/ structure
  - Implemented Firebase integration for data persistence
  - Integrated Google Gemini AI for natural language processing
  - Added Sentence Transformers for local vector embeddings (zero API costs)
  - Separated database seeding into standalone script

## Architecture

### Core Components
1. **FastAPI Application** (`main.py`)
   - RESTful API with OpenAPI documentation
   - CORS middleware for cross-origin requests
   - Health check and query endpoints
   - Graceful error handling

2. **Services Layer**
   - `firebase_service.py`: All Firestore database operations
   - `ai_service.py`: Gemini AI integration for intent classification and response generation

3. **Utils Layer**
   - `embeddings.py`: Sentence Transformer integration for vector embeddings
   - `similarity.py`: Cosine similarity calculations
   - `text_processing.py`: Rank extraction from natural language

4. **Models**
   - Pydantic schemas for request/response validation
   - Type-safe data structures

### Key Features
- **Intent Classification**: Automatically detects query type (rank prediction, cutoffs, FAQs)
- **Vector Search**: Semantic matching using local embeddings (no API costs)
- **Rank Prediction**: Analyzes VITEEE rank and predicts eligible branches with confidence scores
- **Query Logging**: Analytics and monitoring support
- **Fallback Logic**: Graceful degradation when services are unavailable

## Dependencies
- FastAPI + Uvicorn (web framework)
- Firebase Admin SDK (database)
- Google Generative AI (Gemini)
- Sentence Transformers (embeddings)
- NumPy (vector operations)
- Pydantic (validation)

## Configuration
- Environment variables managed through Replit Secrets
- Firebase credentials stored as `firebase-credentials.json`
- Configurable embedding model selection

## User Preferences
None specified yet.

## Next Steps
1. User needs to provide GEMINI_API_KEY secret
2. User needs to upload firebase-credentials.json file
3. Optionally run seed script to populate sample data
4. Test API endpoints via /docs interface
