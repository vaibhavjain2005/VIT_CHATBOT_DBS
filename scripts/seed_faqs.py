import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from services.mongodb_service import MongoDBService
from utils.embeddings import initialize_embedding_model, generate_batch_embeddings

# Load environment variables
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-mpnet-base-v2")

# ============================================================
# SAMPLE FAQ DATA
# ============================================================
SAMPLE_FAQS = [
    {
        "question": "What is VITEEE?",
        "answer": "VITEEE stands for Vellore Institute of Technology Engineering Entrance Examination, which is the entrance test for admission to B.Tech programs at all VIT campuses.",
        "category": "General"
    },
    {
        "question": "How many categories of fees are there at VIT?",
        "answer": "VIT has five categories (Category 1 to Category 5) with varying tuition fees. Category 1 has the lowest fees and highest merit requirement.",
        "category": "Admissions"
    },
    {
        "question": "What is the exam pattern of VITEEE?",
        "answer": "The exam has 125 questions divided into Physics, Chemistry, Mathematics or Biology, English, and Aptitude sections. Each question carries one mark and there is no negative marking.",
        "category": "Exam Pattern"
    },
    {
        "question": "Is there any negative marking in VITEEE?",
        "answer": "No, there is no negative marking in the VITEEE examination.",
        "category": "Exam Pattern"
    },
    {
        "question": "When does VITEEE usually take place?",
        "answer": "VITEEE is typically conducted in April every year, and the application process usually begins in November of the previous year.",
        "category": "Timeline"
    },
    {
        "question": "Can I change my campus after admission?",
        "answer": "No, inter-campus transfers are not allowed once admission has been confirmed at a specific VIT campus.",
        "category": "Policies"
    },
    {
        "question": "How are seats allotted in VIT?",
        "answer": "Seat allotment is based on your VITEEE rank and the availability of seats in your preferred branch and campus during the counselling process.",
        "category": "Counselling"
    },
    {
        "question": "Does VIT offer AI and Data Science programs?",
        "answer": "Yes, VIT offers B.Tech programs in Artificial Intelligence, AI & Data Science, and AI & Robotics across multiple campuses.",
        "category": "Programs"
    }
]

# ============================================================
# FUNCTION TO SEED FAQ DATA
# ============================================================

def seed_faqs(db_service: MongoDBService):
    print("\n" + "="*60)
    print("SEEDING FAQ DATA")
    print("="*60)
    
    initialize_embedding_model(EMBEDDING_MODEL_NAME)

    # Create embedding inputs (use both question + answer)
    texts = [f"Q: {faq['question']} A: {faq['answer']}" for faq in SAMPLE_FAQS]
    print(f"\nGenerating embeddings for {len(texts)} FAQs...")
    embeddings = generate_batch_embeddings(texts)

    for faq, embedding in zip(SAMPLE_FAQS, embeddings):
        faq_data = {
            **faq,
            "embedding": embedding,
            "created_at": datetime.utcnow()
        }

        doc_id = db_service.add_faq(faq_data)
        if doc_id:
            print(f"✅ Added FAQ: {faq['question'][:60]}...")
        else:
            print(f"❌ Failed to add FAQ: {faq['question'][:60]}...")

    print("\n✅ FAQ seeding complete!")

# ============================================================
# MAIN ENTRY POINT
# ============================================================

def main():
    print("\n" + "="*70)
    print("VIT COUNSELING ASSISTANT - FAQ DATABASE SEEDING")
    print("="*70)
    
    db_service = MongoDBService(MONGODB_URL)
    if not db_service.is_connected():
        print("\n❌ Error: Could not connect to MongoDB.")
        return

    response = input("\nThis will add FAQ data to MongoDB. Proceed? (yes/no): ")
    if response.lower() != 'yes':
        print("Seeding cancelled.")
        return

    seed_faqs(db_service)
    
    print("\n" + "="*70)
    print("FAQ SEEDING COMPLETE!")
    print("="*70)

if __name__ == "__main__":
    main()
