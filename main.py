import os
import time
from datetime import datetime
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from models.schemas import QueryRequest, QueryResponse, HealthResponse
from services.firebase_service import FirebaseService
from services.ai_service import AIService
from utils.embeddings import initialize_embedding_model, generate_query_embedding
from utils.text_processing import extract_rank

load_dotenv()

app = FastAPI(
    title="VIT Counseling Assistant API",
    description="AI-powered VIT admission counseling assistant with vector search",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

firebase_service = None
ai_service = None


@app.on_event("startup")
async def startup_event():
    global firebase_service, ai_service
    
    print("=" * 60)
    print("VIT Counseling Assistant API - Starting Up")
    print("=" * 60)
    
    try:
        initialize_embedding_model(EMBEDDING_MODEL_NAME)
    except Exception as e:
        print(f"Warning: Could not initialize embedding model: {e}")
    
    firebase_service = FirebaseService(FIREBASE_CREDENTIALS_PATH)
    
    if GEMINI_API_KEY:
        ai_service = AIService(GEMINI_API_KEY)
    else:
        print("Warning: GEMINI_API_KEY not set. AI features will use fallback logic.")
        ai_service = AIService("")
    
    print("=" * 60)
    print("Startup complete!")
    print("=" * 60)


def predict_branches(rank: int, cutoffs: List[Dict]) -> List[Dict]:
    predictions = []
    
    for cutoff in cutoffs:
        rank_min = cutoff["rank_range"][0]
        rank_max = cutoff["rank_range"][1]
        
        position = (rank - rank_min) / (rank_max - rank_min) if rank_max > rank_min else 0.5
        
        if position <= 0.3:
            confidence = "High"
            confidence_score = 0.9
        elif position <= 0.6:
            confidence = "Good"
            confidence_score = 0.7
        elif position <= 0.85:
            confidence = "Moderate"
            confidence_score = 0.5
        else:
            confidence = "Borderline"
            confidence_score = 0.3
        
        predictions.append({
            "campus": cutoff["campus"],
            "branch": cutoff["branch"],
            "category": cutoff["category"],
            "rank_range": cutoff["rank_range"],
            "confidence": confidence,
            "confidence_score": confidence_score
        })
    
    predictions.sort(key=lambda x: x["confidence_score"], reverse=True)
    return predictions


def format_predictions_for_ai(predictions: List[Dict], rank: int) -> str:
    if not predictions:
        return f"No branch predictions found for rank {rank}."
    
    context = f"Student's VITEEE Rank: {rank}\n\nELIGIBLE BRANCHES:\n\n"
    
    for i, pred in enumerate(predictions[:8], 1):
        context += f"{i}. {pred['branch']} - {pred['campus']}\n"
        context += f"   Category: {pred['category']}\n"
        context += f"   Rank Range: {pred['rank_range'][0]} - {pred['rank_range'][1]}\n"
        context += f"   Admission Chance: {pred['confidence']}\n\n"
    
    return context


@app.get("/", response_model=dict)
async def root():
    return {
        "message": "VIT Counseling Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "query": "/api/query"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "firebase": "connected" if firebase_service and firebase_service.is_connected() else "unavailable",
            "ai": "connected" if ai_service and ai_service.is_available() else "fallback_mode",
            "embeddings": "ready"
        }
    }


@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    start_time = time.time()
    
    query = request.query
    user_id = request.user_id
    
    print(f"\n🔍 Processing: {query}")
    
    intent_result = ai_service.classify_intent(query)
    intent = intent_result["intent"]
    confidence = intent_result["confidence"]
    
    print(f"🎯 Intent: {intent} (confidence: {confidence})")
    
    if confidence < 0.5:
        return QueryResponse(
            answer="Could you clarify if you're asking about cutoffs, hostels, FFCS, or something else?",
            intent="clarification_needed",
            confidence=confidence,
            processing_time_ms=(time.time() - start_time) * 1000
        )
    
    if intent == "rank_prediction":
        rank = extract_rank(query)
        
        if rank:
            print(f"🔢 Rank: {rank}")
            
            cutoffs = firebase_service.get_cutoffs_by_rank(rank)
            
            if cutoffs:
                predictions = predict_branches(rank, cutoffs)
                context = format_predictions_for_ai(predictions, rank)
                
                answer = ai_service.generate_response(query, context, "rank_prediction")
                
                firebase_service.log_query({
                    "query": query,
                    "intent": intent,
                    "rank": rank,
                    "user_id": user_id,
                    "response_length": len(answer)
                })
                
                return QueryResponse(
                    answer=answer,
                    intent="rank_prediction",
                    confidence=confidence,
                    rank_prediction={
                        "rank": rank,
                        "predictions": predictions[:5]
                    },
                    processing_time_ms=(time.time() - start_time) * 1000
                )
            else:
                answer = f"With rank {rank}, I couldn't find predictions. Contact VIT admissions."
                return QueryResponse(
                    answer=answer,
                    intent="rank_prediction",
                    confidence=confidence,
                    processing_time_ms=(time.time() - start_time) * 1000
                )
        else:
            return QueryResponse(
                answer="I couldn't find a rank in your query. Please mention your VITEEE rank.",
                intent="rank_prediction",
                confidence=confidence,
                processing_time_ms=(time.time() - start_time) * 1000
            )
    
    elif intent == "cutoff":
        query_embedding = generate_query_embedding(query)
        cutoff_results = firebase_service.vector_search_cutoffs(query_embedding, top_k=5)
        
        if cutoff_results:
            context = "\n\n".join([
                f"Branch: {r['branch']}, Campus: {r['campus']}, "
                f"Rank Range: {r['rank_range'][0]}-{r['rank_range'][1]}"
                for r in cutoff_results[:3]
            ])
            
            answer = ai_service.generate_response(query, context, "cutoff")
        else:
            answer = "I don't have cutoff information for that query. Please check the official VIT website."
        
        firebase_service.log_query({
            "query": query,
            "intent": intent,
            "user_id": user_id,
            "response_length": len(answer)
        })
        
        return QueryResponse(
            answer=answer,
            intent="cutoff",
            confidence=confidence,
            processing_time_ms=(time.time() - start_time) * 1000
        )
    
    else:
        query_embedding = generate_query_embedding(query)
        faq_results = firebase_service.vector_search_faqs(query_embedding, top_k=3)
        
        if faq_results and faq_results[0]['score'] > 0.7:
            context = "\n\n".join([
                f"Q: {r['question']}\nA: {r['answer']}"
                for r in faq_results[:2]
            ])
            
            answer = ai_service.generate_response(query, context, "faq")
        else:
            answer = "I don't have specific information about that. Please check the official VIT website or contact admissions."
        
        firebase_service.log_query({
            "query": query,
            "intent": intent,
            "user_id": user_id,
            "response_length": len(answer)
        })
        
        return QueryResponse(
            answer=answer,
            intent=intent,
            confidence=confidence,
            processing_time_ms=(time.time() - start_time) * 1000
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
