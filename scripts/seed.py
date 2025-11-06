import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from services.mongodb_service import MongoDBService
from utils.embeddings import initialize_embedding_model, generate_batch_embeddings

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-mpnet-base-v2")

# ============================================================
# COMPREHENSIVE CUTOFF DATA - VELLORE CAMPUS ONLY
# ============================================================
VELLORE_CUTOFFS = [
    # ========== 2024 DATA - CSE Core ==========
    {"year": 2024, "campus": "Vellore", "branch": "Computer Science and Engineering (CSE)", "category": "Category 1", "rank_range": [1, 1840], "notes": "Most competitive branch at VIT"},
    {"year": 2024, "campus": "Vellore", "branch": "Computer Science and Engineering (CSE)", "category": "Category 2", "rank_range": [35, 8280], "notes": "High demand with excellent placements"},
    {"year": 2024, "campus": "Vellore", "branch": "Computer Science and Engineering (CSE)", "category": "Category 3", "rank_range": [41, 12420], "notes": "Competitive entry, strong industry connections"},
    {"year": 2024, "campus": "Vellore", "branch": "Computer Science and Engineering (CSE)", "category": "Category 4", "rank_range": [55, 24800], "notes": "Good placement record"},
    {"year": 2024, "campus": "Vellore", "branch": "Computer Science and Engineering (CSE)", "category": "Category 5", "rank_range": [68, 35100], "notes": "Accessible with solid opportunities"},
    
    # ========== 2024 DATA - CSE (AI/ML) ==========
    {"year": 2024, "campus": "Vellore", "branch": "CSE (Artificial Intelligence and Machine Learning)", "category": "Category 1", "rank_range": [1, 2500], "notes": "Trending specialization, high demand"},
    {"year": 2024, "campus": "Vellore", "branch": "CSE (Artificial Intelligence and Machine Learning)", "category": "Category 2", "rank_range": [46, 8280], "notes": "Excellent career prospects"},
    {"year": 2024, "campus": "Vellore", "branch": "CSE (Artificial Intelligence and Machine Learning)", "category": "Category 3", "rank_range": [46, 16100], "notes": "Popular choice with good placements"},
    {"year": 2024, "campus": "Vellore", "branch": "CSE (Artificial Intelligence and Machine Learning)", "category": "Category 4", "rank_range": [60, 28500], "notes": "Growing industry demand"},
    {"year": 2024, "campus": "Vellore", "branch": "CSE (Artificial Intelligence and Machine Learning)", "category": "Category 5", "rank_range": [75, 38200], "notes": "Future-ready skills"},
    
    # ========== 2024 DATA - CSE (Data Science) ==========
    {"year": 2024, "campus": "Vellore", "branch": "CSE (Data Science)", "category": "Category 1", "rank_range": [1, 2800], "notes": "Analytics and data-focused program"},
    {"year": 2024, "campus": "Vellore", "branch": "CSE (Data Science)", "category": "Category 2", "rank_range": [50, 9100], "notes": "High industry relevance"},
    {"year": 2024, "campus": "Vellore", "branch": "CSE (Data Science)", "category": "Category 3", "rank_range": [46, 16100], "notes": "Strong curriculum alignment"},
    {"year": 2024, "campus": "Vellore", "branch": "CSE (Data Science)", "category": "Category 4", "rank_range": [65, 29800], "notes": "Practical skills development"},
    {"year": 2024, "campus": "Vellore", "branch": "CSE (Data Science)", "category": "Category 5", "rank_range": [80, 39500], "notes": "Career-ready program"},
    
    # ========== 2024 DATA - CSE (IoT) ==========
    {"year": 2024, "campus": "Vellore", "branch": "CSE (Internet of Things)", "category": "Category 1", "rank_range": [1, 3066], "notes": "Emerging technology focus"},
    {"year": 2024, "campus": "Vellore", "branch": "CSE (Internet of Things)", "category": "Category 2", "rank_range": [55, 10200], "notes": "Smart systems and embedded tech"},
    {"year": 2024, "campus": "Vellore", "branch": "CSE (Internet of Things)", "category": "Category 3", "rank_range": [60, 17500], "notes": "Connected devices specialization"},
    {"year": 2024, "campus": "Vellore", "branch": "CSE (Internet of Things)", "category": "Category 4", "rank_range": [70, 31000], "notes": "Industry 4.0 ready"},
    {"year": 2024, "campus": "Vellore", "branch": "CSE (Internet of Things)", "category": "Category 5", "rank_range": [85, 42000], "notes": "Growing field"},
    
    # ========== 2024 DATA - CSE (Cyber Security) ==========
    {"year": 2024, "campus": "Vellore", "branch": "CSE (Cyber Security)", "category": "Category 1", "rank_range": [1, 3200], "notes": "Security-focused curriculum"},
    {"year": 2024, "campus": "Vellore", "branch": "CSE (Cyber Security)", "category": "Category 2", "rank_range": [52, 9800], "notes": "High demand in industry"},
    {"year": 2024, "campus": "Vellore", "branch": "CSE (Cyber Security)", "category": "Category 3", "rank_range": [58, 16800], "notes": "Critical skills training"},
    {"year": 2024, "campus": "Vellore", "branch": "CSE (Cyber Security)", "category": "Category 4", "rank_range": [31, 15300], "notes": "Growing career opportunities"},
    {"year": 2024, "campus": "Vellore", "branch": "CSE (Cyber Security)", "category": "Category 5", "rank_range": [90, 43500], "notes": "Security specialist track"},
    
    # ========== 2024 DATA - CSE (Blockchain) ==========
    {"year": 2024, "campus": "Vellore", "branch": "CSE (Blockchain Technology)", "category": "Category 1", "rank_range": [1, 3500], "notes": "Cutting-edge technology"},
    {"year": 2024, "campus": "Vellore", "branch": "CSE (Blockchain Technology)", "category": "Category 2", "rank_range": [60, 11000], "notes": "Future-focused program"},
    {"year": 2024, "campus": "Vellore", "branch": "CSE (Blockchain Technology)", "category": "Category 3", "rank_range": [70, 18500], "notes": "Innovative curriculum"},
    {"year": 2024, "campus": "Vellore", "branch": "CSE (Blockchain Technology)", "category": "Category 4", "rank_range": [80, 32000], "notes": "Emerging opportunities"},
    {"year": 2024, "campus": "Vellore", "branch": "CSE (Blockchain Technology)", "category": "Category 5", "rank_range": [35, 22425], "notes": "New age technology"},
    
    # ========== 2024 DATA - Information Technology ==========
    {"year": 2024, "campus": "Vellore", "branch": "Information Technology (IT)", "category": "Category 1", "rank_range": [1, 2200], "notes": "Strong IT fundamentals"},
    {"year": 2024, "campus": "Vellore", "branch": "Information Technology (IT)", "category": "Category 2", "rank_range": [45, 9500], "notes": "Software development focus"},
    {"year": 2024, "campus": "Vellore", "branch": "Information Technology (IT)", "category": "Category 3", "rank_range": [50, 14000], "notes": "Industry-aligned curriculum"},
    {"year": 2024, "campus": "Vellore", "branch": "Information Technology (IT)", "category": "Category 4", "rank_range": [62, 27000], "notes": "Good placement record"},
    {"year": 2024, "campus": "Vellore", "branch": "Information Technology (IT)", "category": "Category 5", "rank_range": [78, 36800], "notes": "Solid career path"},
    
    # ========== 2024 DATA - ECE Core ==========
    {"year": 2024, "campus": "Vellore", "branch": "Electronics and Communication Engineering (ECE)", "category": "Category 1", "rank_range": [100, 5500], "notes": "Core electronics with strong labs"},
    {"year": 2024, "campus": "Vellore", "branch": "Electronics and Communication Engineering (ECE)", "category": "Category 2", "rank_range": [123, 22140], "notes": "Traditional choice with good placements"},
    {"year": 2024, "campus": "Vellore", "branch": "Electronics and Communication Engineering (ECE)", "category": "Category 3", "rank_range": [150, 28000], "notes": "Solid foundation in electronics"},
    {"year": 2024, "campus": "Vellore", "branch": "Electronics and Communication Engineering (ECE)", "category": "Category 4", "rank_range": [200, 35000], "notes": "Core branch placements"},
    {"year": 2024, "campus": "Vellore", "branch": "Electronics and Communication Engineering (ECE)", "category": "Category 5", "rank_range": [250, 48000], "notes": "Established program"},
    
    # ========== 2024 DATA - ECE (VLSI) ==========
    {"year": 2024, "campus": "Vellore", "branch": "ECE (VLSI Design)", "category": "Category 1", "rank_range": [120, 6000], "notes": "Chip design specialization"},
    {"year": 2024, "campus": "Vellore", "branch": "ECE (VLSI Design)", "category": "Category 2", "rank_range": [150, 18000], "notes": "Semiconductor industry focus"},
    {"year": 2024, "campus": "Vellore", "branch": "ECE (VLSI Design)", "category": "Category 3", "rank_range": [41, 14320], "notes": "Hardware design skills"},
    {"year": 2024, "campus": "Vellore", "branch": "ECE (VLSI Design)", "category": "Category 4", "rank_range": [180, 26000], "notes": "Growing semiconductor sector"},
    {"year": 2024, "campus": "Vellore", "branch": "ECE (VLSI Design)", "category": "Category 5", "rank_range": [220, 38000], "notes": "IC design opportunities"},
    
    # ========== 2024 DATA - Electrical and Electronics ==========
    {"year": 2024, "campus": "Vellore", "branch": "Electrical and Electronics Engineering (EEE)", "category": "Category 1", "rank_range": [150, 8000], "notes": "Power systems and electronics"},
    {"year": 2024, "campus": "Vellore", "branch": "Electrical and Electronics Engineering (EEE)", "category": "Category 2", "rank_range": [200, 24000], "notes": "Core electrical branch"},
    {"year": 2024, "campus": "Vellore", "branch": "Electrical and Electronics Engineering (EEE)", "category": "Category 3", "rank_range": [250, 32000], "notes": "Traditional engineering"},
    {"year": 2024, "campus": "Vellore", "branch": "Electrical and Electronics Engineering (EEE)", "category": "Category 4", "rank_range": [300, 42000], "notes": "Energy sector focus"},
    {"year": 2024, "campus": "Vellore", "branch": "Electrical and Electronics Engineering (EEE)", "category": "Category 5", "rank_range": [350, 55000], "notes": "Power and control systems"},
    
    # ========== 2024 DATA - Mechanical Engineering ==========
    {"year": 2024, "campus": "Vellore", "branch": "Mechanical Engineering", "category": "Category 1", "rank_range": [1, 20000], "notes": "Core mechanical with automation"},
    {"year": 2024, "campus": "Vellore", "branch": "Mechanical Engineering", "category": "Category 2", "rank_range": [500, 35000], "notes": "Traditional core branch"},
    {"year": 2024, "campus": "Vellore", "branch": "Mechanical Engineering", "category": "Category 3", "rank_range": [800, 45000], "notes": "Manufacturing and design"},
    {"year": 2024, "campus": "Vellore", "branch": "Mechanical Engineering", "category": "Category 4", "rank_range": [1000, 58000], "notes": "Automotive opportunities"},
    {"year": 2024, "campus": "Vellore", "branch": "Mechanical Engineering", "category": "Category 5", "rank_range": [1200, 68000], "notes": "Core engineering skills"},
    
    # ========== 2024 DATA - Civil Engineering ==========
    {"year": 2024, "campus": "Vellore", "branch": "Civil Engineering", "category": "Category 1", "rank_range": [500, 30000], "notes": "Infrastructure and construction"},
    {"year": 2024, "campus": "Vellore", "branch": "Civil Engineering", "category": "Category 2", "rank_range": [800, 50000], "notes": "Traditional civil branch"},
    {"year": 2024, "campus": "Vellore", "branch": "Civil Engineering", "category": "Category 3", "rank_range": [1000, 62000], "notes": "Building and structures"},
    {"year": 2024, "campus": "Vellore", "branch": "Civil Engineering", "category": "Category 4", "rank_range": [1200, 75000], "notes": "Government sector opportunities"},
    
    # ========== 2024 DATA - Chemical Engineering ==========
    {"year": 2024, "campus": "Vellore", "branch": "Chemical Engineering", "category": "Category 1", "rank_range": [400, 28000], "notes": "Process engineering focus"},
    {"year": 2024, "campus": "Vellore", "branch": "Chemical Engineering", "category": "Category 2", "rank_range": [700, 48000], "notes": "Chemical industry"},
    {"year": 2024, "campus": "Vellore", "branch": "Chemical Engineering", "category": "Category 3", "rank_range": [900, 60000], "notes": "Core chemical branch"},
    
    # ========== 2024 DATA - Biotechnology ==========
    {"year": 2024, "campus": "Vellore", "branch": "Biotechnology", "category": "Category 1", "rank_range": [200, 25000], "notes": "Research-oriented program"},
    {"year": 2024, "campus": "Vellore", "branch": "Biotechnology", "category": "Category 2", "rank_range": [300, 54000], "notes": "Life sciences focus"},
    {"year": 2024, "campus": "Vellore", "branch": "Biotechnology", "category": "Category 3", "rank_range": [400, 65000], "notes": "Biotech industry"},
    {"year": 2024, "campus": "Vellore", "branch": "Biotechnology", "category": "Category 4", "rank_range": [500, 78000], "notes": "Research opportunities"},
    
    # ========== 2023 DATA (Previous Year - for trends) ==========
    {"year": 2023, "campus": "Vellore", "branch": "Computer Science and Engineering (CSE)", "category": "Category 1", "rank_range": [1, 1650], "notes": "2023 cutoff"},
    {"year": 2023, "campus": "Vellore", "branch": "Computer Science and Engineering (CSE)", "category": "Category 2", "rank_range": [30, 7800], "notes": "2023 cutoff"},
    {"year": 2023, "campus": "Vellore", "branch": "Computer Science and Engineering (CSE)", "category": "Category 3", "rank_range": [38, 11800], "notes": "2023 cutoff"},
    
    {"year": 2023, "campus": "Vellore", "branch": "CSE (Artificial Intelligence and Machine Learning)", "category": "Category 1", "rank_range": [1, 2300], "notes": "2023 cutoff"},
    {"year": 2023, "campus": "Vellore", "branch": "CSE (Artificial Intelligence and Machine Learning)", "category": "Category 2", "rank_range": [40, 7900], "notes": "2023 cutoff"},
    {"year": 2023, "campus": "Vellore", "branch": "CSE (Artificial Intelligence and Machine Learning)", "category": "Category 3", "rank_range": [43, 15200], "notes": "2023 cutoff"},
    
    {"year": 2023, "campus": "Vellore", "branch": "CSE (Data Science)", "category": "Category 1", "rank_range": [1, 2600], "notes": "2023 cutoff"},
    {"year": 2023, "campus": "Vellore", "branch": "CSE (Data Science)", "category": "Category 2", "rank_range": [45, 8700], "notes": "2023 cutoff"},
    
    {"year": 2023, "campus": "Vellore", "branch": "Electronics and Communication Engineering (ECE)", "category": "Category 1", "rank_range": [95, 5200], "notes": "2023 cutoff"},
    {"year": 2023, "campus": "Vellore", "branch": "Electronics and Communication Engineering (ECE)", "category": "Category 2", "rank_range": [115, 21000], "notes": "2023 cutoff"},
    
    {"year": 2023, "campus": "Vellore", "branch": "Mechanical Engineering", "category": "Category 1", "rank_range": [1, 19000], "notes": "2023 cutoff"},
    {"year": 2023, "campus": "Vellore", "branch": "Mechanical Engineering", "category": "Category 2", "rank_range": [450, 33000], "notes": "2023 cutoff"},
    
    # ========== 2022 DATA (2 Years Ago - for trends) ==========
    {"year": 2022, "campus": "Vellore", "branch": "Computer Science and Engineering (CSE)", "category": "Category 1", "rank_range": [1, 1500], "notes": "2022 cutoff"},
    {"year": 2022, "campus": "Vellore", "branch": "Computer Science and Engineering (CSE)", "category": "Category 2", "rank_range": [25, 7200], "notes": "2022 cutoff"},
    {"year": 2022, "campus": "Vellore", "branch": "Computer Science and Engineering (CSE)", "category": "Category 3", "rank_range": [35, 11000], "notes": "2022 cutoff"},
    
    {"year": 2022, "campus": "Vellore", "branch": "CSE (Artificial Intelligence and Machine Learning)", "category": "Category 1", "rank_range": [1, 2100], "notes": "2022 cutoff"},
    {"year": 2022, "campus": "Vellore", "branch": "CSE (Artificial Intelligence and Machine Learning)", "category": "Category 2", "rank_range": [35, 7400], "notes": "2022 cutoff"},
    
    {"year": 2022, "campus": "Vellore", "branch": "Electronics and Communication Engineering (ECE)", "category": "Category 1", "rank_range": [90, 4900], "notes": "2022 cutoff"},
    {"year": 2022, "campus": "Vellore", "branch": "Electronics and Communication Engineering (ECE)", "category": "Category 2", "rank_range": [110, 19500], "notes": "2022 cutoff"},
    
    {"year": 2022, "campus": "Vellore", "branch": "Mechanical Engineering", "category": "Category 1", "rank_range": [1, 18000], "notes": "2022 cutoff"},
]

# ============================================================
# SEEDING FUNCTION
# ============================================================
def seed_database(db_service: MongoDBService):
    print("\n" + "=" * 60)
    print("🌱 SEEDING VELLORE CAMPUS CUTOFF DATA")
    print("=" * 60)

    initialize_embedding_model(EMBEDDING_MODEL_NAME)
    
    descriptions = [
        f"{c['branch']} at {c['campus']} ({c['category']}) - Year {c['year']}" 
        for c in VELLORE_CUTOFFS
    ]
    
    print(f"\n📊 Generating embeddings for {len(descriptions)} cutoff entries...")
    embeddings = generate_batch_embeddings(descriptions)

    success_count = 0
    fail_count = 0
    
    for cutoff, embedding in zip(VELLORE_CUTOFFS, embeddings):
        cutoff["embedding"] = embedding
        cutoff["last_updated"] = datetime.utcnow()
        doc_id = db_service.add_cutoff(cutoff)
        if doc_id:
            print(f"✅ Added: {cutoff['year']} - {cutoff['branch']} ({cutoff['category']})")
            success_count += 1
        else:
            print(f"❌ Failed: {cutoff['branch']} - {cutoff['category']}")
            fail_count += 1

    print("\n" + "=" * 60)
    print(f"✅ Seeding Complete!")
    print(f"📊 Successfully added: {success_count} entries")
    if fail_count > 0:
        print(f"❌ Failed: {fail_count} entries")
    print("=" * 60)

# ============================================================
# MAIN ENTRY POINT
# ============================================================
def main():
    print("\n" + "=" * 70)
    print("VIT VELLORE CAMPUS - DATABASE SEEDING SCRIPT")
    print("=" * 70)

    db_service = MongoDBService(MONGODB_URL)
    if not db_service.is_connected():
        print("\n❌ Error: Could not connect to MongoDB. Make sure MongoDB is running.")
        return

    print(f"\n📊 This will seed {len(VELLORE_CUTOFFS)} cutoff entries for VIT Vellore campus")
    print("📅 Years: 2022, 2023, 2024")
    print("🏢 Campus: Vellore only")
    print("🎓 Branches: CSE variants, ECE, IT, Mechanical, Civil, Chemical, Bio")
    
    proceed = input("\n⚠️  Proceed with seeding? (yes/no): ").strip().lower()
    if proceed != "yes":
        print("❌ Seeding cancelled.")
        return

    seed_database(db_service)

if __name__ == "__main__":
    main()