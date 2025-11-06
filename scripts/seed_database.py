import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from services.mongodb_service import MongoDBService
from utils.embeddings import initialize_embedding_model, generate_batch_embeddings

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-mpnet-base-v2")

# Sample data with year-wise cutoffs
SAMPLE_CUTOFFS = [
    # 2023 Data
    {
        "year": 2023,
        "campus": "Vellore",
        "branch": "Computer Science and Engineering (CSE)",
        "category": "Category 1",
        "rank_range": [1, 5000],
        "seats": 240,
        "filled": 240,
        "notes": "Most competitive branch with consistent cutoffs"
    },
    {
        "year": 2023,
        "campus": "Chennai",
        "branch": "Computer Science and Engineering (CSE)",
        "category": "Category 1",
        "rank_range": [3000, 8000],
        "seats": 180,
        "filled": 180,
        "notes": "Growing demand for Chennai campus"
    },
    
    # 2024 Data
    {
        "year": 2024,
        "campus": "Vellore",
        "branch": "Computer Science and Engineering (CSE)",
        "category": "Category 1",
        "rank_range": [1, 4500],
        "seats": 260,
        "filled": 260,
        "notes": "Increased competition due to new AI specialization"
    },
    {
        "year": 2024,
        "campus": "Chennai",
        "branch": "Computer Science and Engineering (CSE)",
        "category": "Category 1",
        "rank_range": [2500, 7000],
        "seats": 200,
        "filled": 200,
        "notes": "Improved placement statistics"
    },
    
    # 2025 Data
    {
        "year": 2025,
        "campus": "Vellore",
        "branch": "Computer Science and Engineering (CSE)",
        "category": "Category 1",
        "rank_range": [1, 4000],
        "seats": 280,
        "filled": 280,
        "notes": "Highest competition yet with new industry partnerships"
    },
    {
        "year": 2025,
        "campus": "Chennai",
        "branch": "Computer Science and Engineering (CSE)",
        "category": "Category 1",
        "rank_range": [2000, 6000],
        "seats": 220,
        "filled": 220,
        "notes": "Increased seats and improved infrastructure"
    },
    
    # Similar pattern for other branches
    # ECE Data across years
    {
        "year": 2023,
        "campus": "Vellore",
        "branch": "Electronics and Communication Engineering (ECE)",
        "category": "Category 1",
        "rank_range": [5000, 15000],
        "seats": 180,
        "filled": 175
    },
    {
        "year": 2024,
        "campus": "Vellore",
        "branch": "Electronics and Communication Engineering (ECE)",
        "category": "Category 1",
        "rank_range": [4500, 14000],
        "seats": 180,
        "filled": 180
    },
    {
        "year": 2025,
        "campus": "Vellore",
        "branch": "Electronics and Communication Engineering (ECE)",
        "category": "Category 1",
        "rank_range": [4000, 13000],
        "seats": 190,
        "filled": 190
    }
]

def seed_database(db_service: MongoDBService):
    print("\n" + "="*60)
    print("SEEDING YEAR-WISE CUTOFF DATA")
    print("="*60)
    
    # Initialize embedding model for vector search
    initialize_embedding_model(EMBEDDING_MODEL_NAME)
    
    # Generate embeddings for the cutoff descriptions
    descriptions = [
        f"{c['branch']} at {c['campus']} campus, {c['category']} - Year {c['year']}"
        for c in SAMPLE_CUTOFFS
    ]
    print(f"\nGenerating embeddings for {len(descriptions)} cutoff entries...")
    embeddings = generate_batch_embeddings(descriptions)
    
    # Add embeddings to cutoff data
    for cutoff, embedding in zip(SAMPLE_CUTOFFS, embeddings):
        cutoff_data = {
            **cutoff,
            "embedding": embedding,
            "last_updated": datetime.utcnow()
        }
        
        doc_id = db_service.add_cutoff(cutoff_data)
        if doc_id:
            print(f"✅ Added {cutoff['year']} cutoff: {cutoff['branch']} - {cutoff['campus']}")
        else:
            print(f"❌ Failed to add {cutoff['year']} cutoff: {cutoff['branch']} - {cutoff['campus']}")
    
    print("\n✅ Database seeding complete!")

def main():
    print("\n" + "="*70)
    print("VIT COUNSELING ASSISTANT - YEAR-WISE DATABASE SEEDING")
    print("="*70)
    
    db_service = MongoDBService(MONGODB_URL)
    
    if not db_service.is_connected():
        print("\n❌ Error: Could not connect to MongoDB.")
        print("Please make sure MongoDB is running locally and try again.")
        return
    
    print("\nThis script will add year-wise cutoff data to MongoDB.")
    print("This includes data from 2023-2025 for trend analysis.")
    response = input("Do you want to proceed? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Seeding cancelled.")
        return
    
    seed_database(db_service)
    
    # Display sample trend analysis
    print("\nTesting trend analysis...")
    trends = db_service.get_year_wise_trends(
        branch="Computer Science and Engineering (CSE)",
        campus="Vellore",
        category="Category 1"
    )
    
    if trends:
        print("\nSample Trend Analysis for CSE at Vellore:")
        for trend in trends.get("trends", []):
            print(f"Year {trend['year']}: Range {trend['min_rank']}-{trend['max_rank']}")
            if "yoy_change" in trend:
                print(f"Year-over-year change: {trend['yoy_change']}%")
    
    # Test prediction
    prediction = db_service.predict_rank_range(
        branch="Computer Science and Engineering (CSE)",
        campus="Vellore",
        category="Category 1"
    )
    
    if prediction:
        print(f"\nPredicted 2026 Rank Range:")
        print(f"Min Rank: {prediction['predicted_min_rank']}")
        print(f"Max Rank: {prediction['predicted_max_rank']}")
        print(f"Confidence: {prediction['confidence']}")
        print(f"Trend: {prediction['trend']} ({prediction['avg_yearly_change']}% per year)")
    
    print("\n" + "="*70)
    print("SEEDING AND TESTING COMPLETE!")
    print("="*70)

if __name__ == "__main__":
    main()