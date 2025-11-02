import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from services.firebase_service import FirebaseService
from utils.embeddings import initialize_embedding_model, generate_batch_embeddings

load_dotenv()

FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")


SAMPLE_FAQS = [
    {
        "question": "How are the hostel facilities at VIT?",
        "answer": "VIT offers excellent hostel facilities with AC and non-AC options. Each hostel has 24/7 security, Wi-Fi, mess facilities, and common rooms. The hostels are well-maintained and provide a comfortable living environment for students.",
        "category": "hostel"
    },
    {
        "question": "What is FFCS in VIT?",
        "answer": "FFCS stands for Fully Flexible Credit System. It allows students to choose their courses, faculty, and time slots according to their preferences. This system gives students flexibility in planning their academic schedule and helps them learn at their own pace.",
        "category": "academics"
    },
    {
        "question": "What are the placement statistics at VIT?",
        "answer": "VIT has excellent placement records with top companies like Microsoft, Amazon, Google, and TCS recruiting from campus. The average package varies by branch, with CSE typically seeing higher packages. Over 80% of students get placed through campus recruitment.",
        "category": "placements"
    },
    {
        "question": "What clubs and activities are available at VIT?",
        "answer": "VIT has over 100 student clubs covering technical, cultural, sports, and literary activities. Popular clubs include IEEE, CSI, Riviera (cultural fest), and Gravitas (technical fest). Students can join multiple clubs and actively participate in events throughout the year.",
        "category": "campus_life"
    },
    {
        "question": "What is the fee structure at VIT?",
        "answer": "The fee structure varies by category. Category 1 has the highest fees (around 1.98 lakhs per semester), while Category 5 offers fee waivers based on VITEEE rank. Hostel fees are additional and depend on the type of accommodation chosen.",
        "category": "fees"
    }
]


SAMPLE_CUTOFFS = [
    {
        "campus": "Vellore",
        "branch": "Computer Science and Engineering (CSE)",
        "category": "Category 1",
        "rank_range": [1, 5000],
        "answer": "CSE at VIT Vellore Category 1 typically accepts ranks between 1-5000. This is the most competitive branch."
    },
    {
        "campus": "Vellore",
        "branch": "Electronics and Communication Engineering (ECE)",
        "category": "Category 1",
        "rank_range": [3000, 12000],
        "answer": "ECE at VIT Vellore Category 1 accepts ranks between 3000-12000."
    },
    {
        "campus": "Chennai",
        "branch": "Computer Science and Engineering (CSE)",
        "category": "Category 1",
        "rank_range": [8000, 20000],
        "answer": "CSE at VIT Chennai Category 1 accepts ranks between 8000-20000."
    },
    {
        "campus": "Vellore",
        "branch": "Information Technology (IT)",
        "category": "Category 1",
        "rank_range": [5000, 15000],
        "answer": "IT at VIT Vellore Category 1 accepts ranks between 5000-15000."
    },
    {
        "campus": "Vellore",
        "branch": "Mechanical Engineering",
        "category": "Category 1",
        "rank_range": [10000, 30000],
        "answer": "Mechanical Engineering at VIT Vellore Category 1 accepts ranks between 10000-30000."
    }
]


def seed_faqs(firebase_service: FirebaseService):
    print("\n" + "="*60)
    print("SEEDING FAQs")
    print("="*60)
    
    initialize_embedding_model(EMBEDDING_MODEL_NAME)
    
    questions = [faq["question"] for faq in SAMPLE_FAQS]
    print(f"Generating embeddings for {len(questions)} FAQs...")
    embeddings = generate_batch_embeddings(questions)
    
    for faq, embedding in zip(SAMPLE_FAQS, embeddings):
        faq_data = {
            **faq,
            "embedding": embedding
        }
        
        doc_id = firebase_service.add_faq(faq_data)
        if doc_id:
            print(f"✅ Added FAQ: {faq['question'][:50]}...")
        else:
            print(f"❌ Failed to add FAQ: {faq['question'][:50]}...")
    
    print("\n✅ FAQ seeding complete!")


def seed_cutoffs(firebase_service: FirebaseService):
    print("\n" + "="*60)
    print("SEEDING CUTOFFS")
    print("="*60)
    
    initialize_embedding_model(EMBEDDING_MODEL_NAME)
    
    answers = [cutoff["answer"] for cutoff in SAMPLE_CUTOFFS]
    print(f"Generating embeddings for {len(answers)} cutoffs...")
    embeddings = generate_batch_embeddings(answers)
    
    for cutoff, embedding in zip(SAMPLE_CUTOFFS, embeddings):
        cutoff_data = {
            **cutoff,
            "embedding": embedding
        }
        
        doc_id = firebase_service.add_cutoff(cutoff_data)
        if doc_id:
            print(f"✅ Added cutoff: {cutoff['branch']} - {cutoff['campus']}")
        else:
            print(f"❌ Failed to add cutoff: {cutoff['branch']} - {cutoff['campus']}")
    
    print("\n✅ Cutoff seeding complete!")


def main():
    print("\n" + "="*70)
    print("VIT COUNSELING ASSISTANT - DATABASE SEEDING SCRIPT")
    print("="*70)
    
    if not os.path.exists(FIREBASE_CREDENTIALS_PATH):
        print(f"\n❌ Error: Firebase credentials file not found at: {FIREBASE_CREDENTIALS_PATH}")
        print("Please upload your firebase-credentials.json file before running this script.")
        return
    
    firebase_service = FirebaseService(FIREBASE_CREDENTIALS_PATH)
    
    if not firebase_service.is_connected():
        print("\n❌ Error: Could not connect to Firebase.")
        print("Please check your credentials and try again.")
        return
    
    print("\nThis script will add sample FAQs and cutoff data to your Firebase database.")
    response = input("Do you want to proceed? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Seeding cancelled.")
        return
    
    seed_faqs(firebase_service)
    seed_cutoffs(firebase_service)
    
    print("\n" + "="*70)
    print("DATABASE SEEDING COMPLETE!")
    print("="*70)
    print("\nYou can now start the API server and test queries.")


if __name__ == "__main__":
    main()
