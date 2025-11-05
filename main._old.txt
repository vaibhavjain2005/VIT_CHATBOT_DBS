import os
import time
from datetime import datetime
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from models.schemas import QueryRequest, QueryResponse, HealthResponse
from services.mongodb_service import MongoDBService
from services.ai_service import AIService
from utils.embeddings import initialize_embedding_model, generate_query_embedding
from utils.text_processing import extract_rank, extract_year

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
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-mpnet-base-v2")

db_service = None
ai_service = None


@app.on_event("startup")
async def startup_event():
    global db_service, ai_service
    
    print("=" * 60)
    print("VIT Counseling Assistant API - Starting Up")
    print("=" * 60)
    
    try:
        initialize_embedding_model(EMBEDDING_MODEL_NAME)
    except Exception as e:
        print(f"Warning: Could not initialize embedding model: {e}")
    
    db_service = MongoDBService(MONGODB_URL)
    
    if GEMINI_API_KEY or GROQ_API_KEY:
        ai_service = AIService(GEMINI_API_KEY, GROQ_API_KEY)
        if GROQ_API_KEY:
            print("GROQ API key found - will attempt to use GROQ as primary LLM")
    else:
        print("Warning: Neither GEMINI_API_KEY nor GROQ_API_KEY set. AI features will use fallback logic.")
        ai_service = AIService("", "")
    
    print("=" * 60)
    print("Startup complete!")
    print("=" * 60)


def predict_branches(rank: int, cutoffs: List[Dict]) -> List[Dict]:
    predictions = []
    
    for cutoff in cutoffs:
        rank_min = cutoff["rank_range"][0]
        rank_max = cutoff["rank_range"][1]
        
        # Calculate relative position and distance
        if rank >= rank_min and rank <= rank_max:
            # Within range - calculate position within range
            position = (rank - rank_min) / (rank_max - rank_min)
            if position <= 0.3:
                confidence = "Very High"
                confidence_score = 0.95
            elif position <= 0.6:
                confidence = "High"
                confidence_score = 0.85
            elif position <= 0.85:
                confidence = "Good"
                confidence_score = 0.75
            else:
                confidence = "Moderate"
                confidence_score = 0.6
        else:
            # Outside range - calculate distance-based confidence
            if rank < rank_min:
                distance = rank_min - rank
                if distance <= 1000:
                    confidence = "Possible"
                    confidence_score = 0.4
                elif distance <= 2000:
                    confidence = "Low"
                    confidence_score = 0.2
                else:
                    confidence = "Very Low"
                    confidence_score = 0.1
            else:  # rank > rank_max
                distance = rank - rank_max
                if distance <= 1000:
                    confidence = "Possible"
                    confidence_score = 0.4
                elif distance <= 2000:
                    confidence = "Low"
                    confidence_score = 0.2
                else:
                    confidence = "Very Low"
                    confidence_score = 0.1
        trend = cutoff.get("trend", {})
        historical = trend.get("historical", [])
        prediction = trend.get("prediction", {})
        # ✅ Add trend data from cutoff
        predictions.append({
            "campus": cutoff["campus"],
            "branch": cutoff["branch"],
            "category": cutoff["category"],
            "year": cutoff.get("year"),  # ✅ Add year
            "rank_range": cutoff["rank_range"],
            "seats": cutoff.get("seats"),  # ✅ Add seats
            "filled": cutoff.get("filled"),  # ✅ Add filled
            "confidence": confidence,
            "confidence_score": confidence_score,
             # ✅ Add trend data
            "historical_trends": historical,
            "prediction": prediction
        })
    
    predictions.sort(key=lambda x: x["confidence_score"], reverse=True)
    return predictions

def format_predictions_for_ai(predictions: List[Dict], rank: int, db_service: MongoDBService) -> str:
    if not predictions:
        return f"No branch predictions found for rank {rank}. Please check the VIT official website for the most up-to-date information."
    
    context = f"Student's VITEEE Rank: {rank}\n\nELIGIBLE BRANCHES:\n\n"
    
    for i, pred in enumerate(predictions[:8], 1):
        # Get historical trends
        trends = db_service.get_year_wise_trends(
            branch=pred['branch'],
            campus=pred['campus'],
            category=pred['category']
        )
        
        # Get future prediction
        prediction = db_service.predict_rank_range(
            branch=pred['branch'],
            campus=pred['campus'],
            category=pred['category']
        )
        
        context += f"{i}. {pred['branch']} - {pred['campus']}\n"
        context += f"   Category: {pred['category']}\n"
        context += f"   Current Rank Range: {pred['rank_range'][0]} - {pred['rank_range'][1]}\n"
        context += f"   Admission Chance: {pred['confidence']}\n"
        
        if trends and trends.get("trends"):
            latest_trends = trends["trends"][-2:]  # Last 2 years
            context += f"   Historical Trend: "
            for trend in latest_trends:
                context += f"{trend['year']}: {trend['min_rank']}-{trend['max_rank']} | "
            context += "\n"
        
        if prediction:
            context += f"   2026 Prediction: {prediction['predicted_min_rank']}-{prediction['predicted_max_rank']}\n"
            context += f"   Trend: {prediction['trend']} ({prediction['avg_yearly_change']}% per year)\n"
            context += f"   Prediction Confidence: {prediction['confidence']}\n"
        
        context += "\n"
    
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
            "database": "connected" if db_service and db_service.is_connected() else "unavailable",
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
        year = extract_year(query) or request.year  # Get year from request
        if rank:
            print(f"🔢 Rank: {rank}, Year: {year}")

            cutoffs = db_service.get_cutoffs_by_rank(rank, year=year)
            
            if cutoffs:
                predictions = predict_branches(rank, cutoffs)
                context = format_predictions_for_ai(predictions, rank, db_service)
                
                answer = ai_service.generate_response(query, context, "rank_prediction")
                
                db_service.log_query({
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
                    year=year or db_service.get_latest_year(),
                    rank_prediction={
                        "rank": rank,
                        "predictions": predictions
                    },
                    has_historical_data=any(len(p.get("historical_trends", [])) > 0 for p in predictions[:5]),
                    has_prediction=any(p.get("prediction") is not None for p in predictions[:5]),
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
        cutoff_results = db_service.vector_search_cutoffs(query_embedding, top_k=5)
        
        if cutoff_results:
            context = "\n\n".join([
                f"Branch: {r['branch']}, Campus: {r['campus']}, "
                f"Rank Range: {r['rank_range'][0]}-{r['rank_range'][1]}"
                for r in cutoff_results[:3]
            ])
            
            answer = ai_service.generate_response(query, context, "cutoff")
        else:
            answer = "I don't have cutoff information for that query. Please check the official VIT website."
        
        db_service.log_query({
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
        faq_results = db_service.vector_search_faqs(query_embedding, top_k=3)
        
        if faq_results and faq_results[0]['score'] > 0.7:
            context = "\n\n".join([
                f"Q: {r['question']}\nA: {r['answer']}"
                for r in faq_results[:2]
            ])
            
            answer = ai_service.generate_response(query, context, "faq")
        else:
            answer = "I don't have specific information about that. Please check the official VIT website or contact admissions."
        
        db_service.log_query({
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
