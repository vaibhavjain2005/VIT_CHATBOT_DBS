# import os
# import time
# from datetime import datetime
# from typing import List, Dict
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from dotenv import load_dotenv

# from models.schemas import QueryRequest, QueryResponse, HealthResponse
# from services.mongodb_service import MongoDBService
# from services.ai_service import AIService
# from utils.embeddings import initialize_embedding_model, generate_query_embedding
# from utils.text_processing import extract_rank, extract_year

# load_dotenv()

# app = FastAPI(
#     title="VIT Counseling Assistant API",
#     description="AI-powered VIT admission counseling assistant with vector search",
#     version="1.0.0"
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
# GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
# MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
# EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-mpnet-base-v2")

# db_service = None
# ai_service = None


# @app.on_event("startup")
# async def startup_event():
#     global db_service, ai_service
    
#     print("=" * 60)
#     print("VIT Counseling Assistant API - Starting Up")
#     print("=" * 60)
    
#     try:
#         initialize_embedding_model(EMBEDDING_MODEL_NAME)
#         print(f"✅ Embedding model initialized: {EMBEDDING_MODEL_NAME}")
#     except Exception as e:
#         print(f"⚠️  Warning: Could not initialize embedding model: {e}")
    
#     db_service = MongoDBService(MONGODB_URL)
    
#     if GEMINI_API_KEY or GROQ_API_KEY:
#         ai_service = AIService(GEMINI_API_KEY, GROQ_API_KEY)
#         if GROQ_API_KEY:
#             print("✅ GROQ API key found - will attempt to use GROQ as primary LLM")
#     else:
#         print("⚠️  Warning: Neither GEMINI_API_KEY nor GROQ_API_KEY set. AI features will use fallback logic.")
#         ai_service = AIService("", "")
    
#     print("=" * 60)
#     print("✅ Startup complete!")
#     print("=" * 60)


# def predict_branches(rank: int, cutoffs: List[Dict]) -> List[Dict]:
#     """Predict branch eligibility based on rank - NO seat filtering"""
#     predictions = []
    
#     for cutoff in cutoffs:
#         rank_min = cutoff["rank_range"][0]
#         rank_max = cutoff["rank_range"][1]
        
#         # Calculate relative position and distance
#         if rank >= rank_min and rank <= rank_max:
#             # Within range - calculate position within range
#             position = (rank - rank_min) / (rank_max - rank_min)
#             if position <= 0.3:
#                 confidence = "Very High"
#                 confidence_score = 0.95
#             elif position <= 0.6:
#                 confidence = "High"
#                 confidence_score = 0.85
#             elif position <= 0.85:
#                 confidence = "Good"
#                 confidence_score = 0.75
#             else:
#                 confidence = "Moderate"
#                 confidence_score = 0.6
#         else:
#             # Outside range - calculate distance-based confidence
#             if rank < rank_min:
#                 distance = rank_min - rank
#                 if distance <= 1000:
#                     confidence = "Possible"
#                     confidence_score = 0.4
#                 elif distance <= 2000:
#                     confidence = "Low"
#                     confidence_score = 0.2
#                 else:
#                     confidence = "Very Low"
#                     confidence_score = 0.1
#             else:  # rank > rank_max
#                 distance = rank - rank_max
#                 if distance <= 1000:
#                     confidence = "Possible"
#                     confidence_score = 0.4
#                 elif distance <= 2000:
#                     confidence = "Low"
#                     confidence_score = 0.2
#                 else:
#                     confidence = "Very Low"
#                     confidence_score = 0.1
        
#         trend = cutoff.get("trend", {})
#         historical = trend.get("historical", [])
#         prediction = trend.get("prediction", {})
        
#         predictions.append({
#             "campus": cutoff["campus"],
#             "branch": cutoff["branch"],
#             "category": cutoff["category"],
#             "year": cutoff.get("year"),
#             "rank_range": cutoff["rank_range"],
#             "confidence": confidence,
#             "confidence_score": confidence_score,
#             "historical_trends": historical,
#             "prediction": prediction
#         })
    
#     predictions.sort(key=lambda x: x["confidence_score"], reverse=True)
#     return predictions


# def format_predictions_for_ai(predictions: List[Dict], rank: int, db_service: MongoDBService) -> str:
#     if not predictions:
#         return f"No branch predictions found for rank {rank}. Please check the VIT official website for the most up-to-date information."
    
#     context = f"Student's VITEEE Rank: {rank}\n\nELIGIBLE BRANCHES (Showing ALL possibilities):\n\n"
    
#     # Show up to 15 branches for comprehensive view
#     for i, pred in enumerate(predictions[:15], 1):
#         # Get historical trends
#         trends = db_service.get_year_wise_trends(
#             branch=pred['branch'],
#             campus=pred['campus'],
#             category=pred['category']
#         )
        
#         # Get future prediction
#         prediction = db_service.predict_rank_range(
#             branch=pred['branch'],
#             campus=pred['campus'],
#             category=pred['category']
#         )
        
#         context += f"{i}. {pred['branch']} - {pred['campus']}\n"
#         context += f"   Category: {pred['category']}\n"
#         context += f"   Current Rank Range: {pred['rank_range'][0]} - {pred['rank_range'][1]}\n"
#         context += f"   Admission Chance: {pred['confidence']}\n"
        
#         if trends and trends.get("trends"):
#             latest_trends = trends["trends"][-2:]  # Last 2 years
#             context += f"   Historical Trend: "
#             for trend in latest_trends:
#                 context += f"{trend['year']}: {trend['min_rank']}-{trend['max_rank']} | "
#             context += "\n"
        
#         if prediction:
#             context += f"   2026 Prediction: {prediction['predicted_min_rank']}-{prediction['predicted_max_rank']}\n"
#             context += f"   Trend: {prediction['trend']} ({prediction['avg_yearly_change']}% per year)\n"
#             context += f"   Prediction Confidence: {prediction['confidence']}\n"
        
#         context += "\n"
    
#     return context


# @app.get("/", response_model=dict)
# async def root():
#     return {
#         "message": "VIT Counseling Assistant API",
#         "version": "1.0.0",
#         "endpoints": {
#             "health": "/health",
#             "query": "/api/query"
#         }
#     }


# @app.get("/health", response_model=HealthResponse)
# async def health_check():
#     return {
#         "status": "healthy",
#         "timestamp": datetime.utcnow().isoformat(),
#         "services": {
#             "database": "connected" if db_service and db_service.is_connected() else "unavailable",
#             "ai": "connected" if ai_service and ai_service.is_available() else "fallback_mode",
#             "embeddings": "ready"
#         }
#     }


# @app.post("/api/query", response_model=QueryResponse)
# async def process_query(request: QueryRequest):
#     start_time = time.time()
    
#     query = request.query
#     user_id = request.user_id
    
#     print(f"\n🔍 Processing: {query}")
    
#     intent_result = ai_service.classify_intent(query)
#     intent = intent_result["intent"]
#     confidence = intent_result["confidence"]
    
#     print(f"🎯 Intent: {intent} (confidence: {confidence})")
    
#     if confidence < 0.5:
#         return QueryResponse(
#             answer="Could you clarify if you're asking about cutoffs, hostels, FFCS, or something else?",
#             intent="clarification_needed",
#             confidence=confidence,
#             processing_time_ms=(time.time() - start_time) * 1000
#         )
    
#     if intent == "rank_prediction":
#         rank = extract_rank(query)
#         year = extract_year(query) or request.year
#         if rank:
#             print(f"🔢 Rank: {rank}, Year: {year}")

#             cutoffs = db_service.get_cutoffs_by_rank(rank, year=year)
            
#             if cutoffs:
#                 predictions = predict_branches(rank, cutoffs)
#                 context = format_predictions_for_ai(predictions, rank, db_service)
                
#                 answer = ai_service.generate_response(query, context, "rank_prediction")
                
#                 db_service.log_query({
#                     "query": query,
#                     "intent": intent,
#                     "rank": rank,
#                     "user_id": user_id,
#                     "response_length": len(answer),
#                     "results_count": len(predictions)
#                 })
                
#                 return QueryResponse(
#                     answer=answer,
#                     intent="rank_prediction",
#                     confidence=confidence,
#                     year=year or db_service.get_latest_year(),
#                     rank_prediction={
#                         "rank": rank,
#                         "predictions": predictions
#                     },
#                     has_historical_data=any(len(p.get("historical_trends", [])) > 0 for p in predictions[:5]),
#                     has_prediction=any(p.get("prediction") is not None for p in predictions[:5]),
#                     processing_time_ms=(time.time() - start_time) * 1000
#                 )
#             else:
#                 answer = f"With rank {rank}, I couldn't find predictions. Contact VIT admissions."
#                 return QueryResponse(
#                     answer=answer,
#                     intent="rank_prediction",
#                     confidence=confidence,
#                     processing_time_ms=(time.time() - start_time) * 1000
#                 )
#         else:
#             return QueryResponse(
#                 answer="I couldn't find a rank in your query. Please mention your VITEEE rank.",
#                 intent="rank_prediction",
#                 confidence=confidence,
#                 processing_time_ms=(time.time() - start_time) * 1000
#             )
    
#     elif intent == "cutoff":
#         query_embedding = generate_query_embedding(query)
#         cutoff_results = db_service.vector_search_cutoffs(query_embedding, top_k=5)
        
#         if cutoff_results:
#             context = "\n\n".join([
#                 f"Branch: {r['branch']}, Campus: {r['campus']}, "
#                 f"Rank Range: {r['rank_range'][0]}-{r['rank_range'][1]}"
#                 for r in cutoff_results[:3]
#             ])
            
#             answer = ai_service.generate_response(query, context, "cutoff")
#         else:
#             answer = "I don't have cutoff information for that query. Please check the official VIT website."
        
#         db_service.log_query({
#             "query": query,
#             "intent": intent,
#             "user_id": user_id,
#             "response_length": len(answer),
#             "results_count": len(cutoff_results)
#         })
        
#         return QueryResponse(
#             answer=answer,
#             intent="cutoff",
#             confidence=confidence,
#             processing_time_ms=(time.time() - start_time) * 1000
#         )
    
#     else:  # FAQ intent
#         query_embedding = generate_query_embedding(query)
#         # Get MORE FAQs for better AI context (increased from 3 to 5)
#         faq_results = db_service.vector_search_faqs(query_embedding, top_k=5)
        
#         if faq_results and faq_results[0]['score'] > 0.5:
#             # Provide ALL relevant FAQ context to AI
#             context = "RELEVANT FAQ INFORMATION:\n\n"
#             for i, r in enumerate(faq_results, 1):
#                 context += f"{i}. Q: {r['question']}\n   A: {r['answer']}\n   (Relevance: {r['score']:.2f})\n\n"
            
#             # Let AI generate answer using ALL the FAQ information
#             answer = ai_service.generate_response(query, context, "faq")
#         else:
#             answer = "I don't have specific information about that. Please check the official VIT website or contact admissions."
        
#         db_service.log_query({
#             "query": query,
#             "intent": intent,
#             "user_id": user_id,
#             "response_length": len(answer),
#             "results_count": len(faq_results)
#         })
        
#         return QueryResponse(
#             answer=answer,
#             intent=intent,
#             confidence=confidence,
#             processing_time_ms=(time.time() - start_time) * 1000
#         )


# if __name__ == "__main__":
#     import uvicorn
#     port = int(os.getenv("PORT", 5000))
#     uvicorn.run(app, host="0.0.0.0", port=port)


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
    description="AI-powered VIT admission counseling assistant with 2025 predictions",
    version="2.0.0"
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
        print(f"✅ Embedding model initialized: {EMBEDDING_MODEL_NAME}")
    except Exception as e:
        print(f"⚠️ Warning: Could not initialize embedding model: {e}")
    
    db_service = MongoDBService(MONGODB_URL)
    
    if GEMINI_API_KEY or GROQ_API_KEY:
        ai_service = AIService(GEMINI_API_KEY, GROQ_API_KEY)
        if GROQ_API_KEY:
            print("✅ GROQ API key found - will attempt to use GROQ as primary LLM")
    else:
        print("⚠️ Warning: Neither GEMINI_API_KEY nor GROQ_API_KEY set. AI features will use fallback logic.")
        ai_service = AIService("", "")
    
    print("=" * 60)
    print("✅ Startup complete!")
    print("=" * 60)


def predict_2025_cutoffs(historical_data: List[Dict], branch: str, campus: str, category: str) -> Dict:
    """Predict 2025 cutoffs based on 2023 and 2024 trends"""
    if len(historical_data) < 2:
        return None
    
    # Sort by year
    historical_data.sort(key=lambda x: x['year'])
    
    # Get 2023 and 2024 data
    data_2023 = next((d for d in historical_data if d['year'] == 2023), None)
    data_2024 = next((d for d in historical_data if d['year'] == 2024), None)
    
    if not data_2023 or not data_2024:
        return None
    
    # Calculate trend
    rank_2023_min, rank_2023_max = data_2023['rank_range']
    rank_2024_min, rank_2024_max = data_2024['rank_range']
    
    # Calculate average change
    min_change = rank_2024_min - rank_2023_min
    max_change = rank_2024_max - rank_2023_max
    
    # Predict 2025 (extrapolate trend)
    predicted_min = rank_2024_min + min_change
    predicted_max = rank_2024_max + max_change
    
    # Add some buffer (±5%) for safety
    buffer = int((predicted_max - predicted_min) * 0.05)
    predicted_min = max(1, predicted_min - buffer)
    predicted_max = predicted_max + buffer
    
    # Determine confidence based on trend consistency
    consistency = 1 - (abs(min_change) / max(rank_2023_min, 1)) if rank_2023_min > 0 else 0.5
    confidence = max(0.6, min(0.85, consistency))
    
    return {
        'year': 2025,
        'campus': campus,
        'branch': branch,
        'category': category,
        'rank_range': [predicted_min, predicted_max],
        'confidence': confidence,
        'is_prediction': True,
        'notes': f'Predicted based on 2023-2024 trends (Confidence: {int(confidence*100)}%)',
        'historical_data': {
            '2023': [rank_2023_min, rank_2023_max],
            '2024': [rank_2024_min, rank_2024_max]
        }
    }


def simple_predictions(rank: int, cutoffs: List[Dict], year: int) -> List[Dict]:
    """Enhanced prediction logic with 2025 predictions"""
    predictions = []
    
    for cutoff in cutoffs:
        rank_min = cutoff["rank_range"][0]
        rank_max = cutoff["rank_range"][1]
        is_prediction = cutoff.get('is_prediction', False)
        
        # Adjust confidence for predictions
        confidence_multiplier = 0.9 if is_prediction else 1.0
        
        # Simple confidence based on position
        if rank >= rank_min and rank <= rank_max:
            position = (rank - rank_min) / (rank_max - rank_min)
            if position <= 0.3:
                confidence = "Very High"
                confidence_score = 0.95 * confidence_multiplier
            elif position <= 0.6:
                confidence = "High"
                confidence_score = 0.85 * confidence_multiplier
            else:
                confidence = "Good"
                confidence_score = 0.70 * confidence_multiplier
        elif rank < rank_min:
            confidence = "Excellent"
            confidence_score = 0.98 * confidence_multiplier
        else:
            distance = rank - rank_max
            if distance <= 2000:
                confidence = "Possible"
                confidence_score = 0.50 * confidence_multiplier
            else:
                confidence = "Low"
                confidence_score = 0.30 * confidence_multiplier
        
        predictions.append({
            "campus": cutoff["campus"],
            "branch": cutoff["branch"],
            "category": cutoff["category"],
            "year": cutoff.get("year"),
            "rank_range": cutoff["rank_range"],
            "confidence": confidence,
            "confidence_score": confidence_score,
            "notes": cutoff.get("notes", ""),
            "is_prediction": is_prediction,
            "historical_data": cutoff.get("historical_data")
        })
    
    # Sort by confidence
    predictions.sort(key=lambda x: x["confidence_score"], reverse=True)
    return predictions


def format_cutoffs_for_llm(predictions: List[Dict], rank: int, year: int) -> str:
    """Format predictions for LLM including 2025 predictions"""
    if not predictions:
        return f"No cutoff data found for rank {rank}."
    
    is_2025 = year == 2025
    context = f"Student's VITEEE Rank: {rank}\n"
    context += f"Query Year: {year}\n\n"
    
    if is_2025:
        context += "⚠️ NOTE: 2025 cutoffs are PREDICTIONS based on 2023-2024 trends\n\n"
    
    context += "AVAILABLE BRANCHES (sorted by eligibility):\n\n"
    
    # Show top 15 branches
    for i, pred in enumerate(predictions[:15], 1):
        rank_min, rank_max = pred['rank_range']
        is_pred = pred.get('is_prediction', False)
        
        context += f"{i}. {pred['branch']} - {pred['campus']}\n"
        context += f"   Category: {pred['category']}\n"
        
        if is_pred:
            context += f"   📊 PREDICTED for 2025: {rank_min} - {rank_max}\n"
            if pred.get('historical_data'):
                hist = pred['historical_data']
                context += f"   Historical: 2023({hist['2023'][0]}-{hist['2023'][1]}), "
                context += f"2024({hist['2024'][0]}-{hist['2024'][1]})\n"
        else:
            context += f"   Year: {pred.get('year', 'N/A')}\n"
            context += f"   Cutoff Range: {rank_min} - {rank_max}\n"
        
        # Add position context
        if rank < rank_min:
            context += f"   ✅ Student's rank is BETTER (by {rank_min - rank} ranks)\n"
        elif rank <= rank_max:
            context += f"   ✅ Student's rank is WITHIN range\n"
        else:
            context += f"   ⚠ Student's rank is {rank - rank_max} ranks below cutoff\n"
        
        if pred.get('notes'):
            context += f"   Note: {pred['notes']}\n"
        
        context += "\n"
    
    return context


@app.get("/", response_model=dict)
async def root():
    return {
        "message": "VIT Counseling Assistant API with 2025 Predictions",
        "version": "2.0.0",
        "features": ["2025 Cutoff Predictions", "Historical Trend Analysis"],
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
            "embeddings": "ready",
            "predictions": "enabled"
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
            answer="Could you clarify if you're asking about cutoffs, rank predictions, or something else?",
            intent="clarification_needed",
            confidence=confidence,
            processing_time_ms=(time.time() - start_time) * 1000
        )
    
    if intent == "rank_prediction":
        rank = extract_rank(query)
        year = extract_year(query) or request.year or 2025  # Default to 2025
        
        if rank:
            print(f"🔢 Rank: {rank}, Year: {year}")
            
            # If querying for 2025, generate predictions from historical data
            if year == 2025:
                print("📊 Generating 2025 predictions from historical data...")
                
                # Get ALL historical data (all years in database)
                all_historical = db_service.get_all_cutoffs_for_rank(rank)
                
                if all_historical:
                    # Group by branch+campus+category to get historical data
                    branch_groups = {}
                    for cutoff in all_historical:
                        key = f"{cutoff['branch']}_{cutoff['campus']}_{cutoff['category']}"
                        if key not in branch_groups:
                            branch_groups[key] = []
                        branch_groups[key].append(cutoff)
                    
                    # Generate predictions for each branch
                    predicted_cutoffs = []
                    for key, historical in branch_groups.items():
                        if len(historical) >= 2:  # Need at least 2 years
                            branch = historical[0]['branch']
                            campus = historical[0]['campus']
                            category = historical[0]['category']
                            
                            prediction = predict_2025_cutoffs(historical, branch, campus, category)
                            if prediction:
                                predicted_cutoffs.append(prediction)
                    
                    cutoffs = predicted_cutoffs
                    print(f"✅ Generated {len(predicted_cutoffs)} predictions for 2025")
                else:
                    cutoffs = []
                    print("⚠️ No historical data found for 2023-2024")
            else:
                # Get cutoff data for specific historical year
                cutoffs = db_service.get_cutoffs_by_rank(rank, year=year)
            
            if cutoffs:
                # Create predictions
                predictions = simple_predictions(rank, cutoffs, year)
                
                # Format for LLM
                context = format_cutoffs_for_llm(predictions, rank, year)
                
                # Let LLM generate natural response
                answer = ai_service.generate_response(query, context, "rank_prediction")
                
                db_service.log_query({
                    "query": query,
                    "intent": intent,
                    "rank": rank,
                    "year": year,
                    "user_id": user_id,
                    "response_length": len(answer),
                    "results_count": len(predictions),
                    "is_prediction": year == 2025
                })
                
                return QueryResponse(
                    answer=answer,
                    intent="rank_prediction",
                    confidence=confidence,
                    year=year,
                    rank_prediction={
                        "rank": rank,
                        "predictions": predictions[:15],
                        "is_prediction_year": year == 2025
                    },
                    processing_time_ms=(time.time() - start_time) * 1000
                )
            else:
                answer = f"I couldn't find cutoff data for rank {rank} in {year}. "
                if year == 2025:
                    answer += "Unable to generate predictions due to insufficient historical data."
                return QueryResponse(
                    answer=answer,
                    intent="rank_prediction",
                    confidence=confidence,
                    processing_time_ms=(time.time() - start_time) * 1000
                )
        else:
            return QueryResponse(
                answer="I couldn't find a rank in your query. Please mention your VITEEE rank (e.g., 'My rank is 15000').",
                intent="rank_prediction",
                confidence=confidence,
                processing_time_ms=(time.time() - start_time) * 1000
            )
    
    elif intent == "cutoff":
        query_embedding = generate_query_embedding(query)
        cutoff_results = db_service.vector_search_cutoffs(query_embedding, top_k=5)
        
        if cutoff_results:
            context = "CUTOFF INFORMATION:\n\n"
            for i, r in enumerate(cutoff_results[:5], 1):
                context += f"{i}. Branch: {r['branch']}, Campus: {r['campus']}\n"
                context += f"   Category: {r['category']}\n"
                context += f"   Rank Range: {r['rank_range'][0]}-{r['rank_range'][1]}\n"
                context += f"   Relevance: {r['score']:.2f}\n\n"
            
            answer = ai_service.generate_response(query, context, "cutoff")
        else:
            answer = "I don't have cutoff information for that query. Please check the official VIT website."
        
        db_service.log_query({
            "query": query,
            "intent": intent,
            "user_id": user_id,
            "response_length": len(answer),
            "results_count": len(cutoff_results)
        })
        
        return QueryResponse(
            answer=answer,
            intent="cutoff",
            confidence=confidence,
            processing_time_ms=(time.time() - start_time) * 1000
        )
    
    else:  # FAQ intent
        query_embedding = generate_query_embedding(query)
        faq_results = db_service.vector_search_faqs(query_embedding, top_k=5)
        
        if faq_results and faq_results[0]['score'] > 0.5:
            context = "RELEVANT FAQ INFORMATION:\n\n"
            for i, r in enumerate(faq_results, 1):
                context += f"{i}. Q: {r['question']}\n   A: {r['answer']}\n   (Relevance: {r['score']:.2f})\n\n"
            
            answer = ai_service.generate_response(query, context, "faq")
        else:
            answer = "I don't have specific information about that. Please check the official VIT website or contact admissions."
        
        db_service.log_query({
            "query": query,
            "intent": intent,
            "user_id": user_id,
            "response_length": len(answer),
            "results_count": len(faq_results)
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