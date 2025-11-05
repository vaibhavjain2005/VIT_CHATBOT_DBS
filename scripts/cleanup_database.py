from pymongo import MongoClient
import os
from dotenv import load_dotenv
import sys

def cleanup_database():
    # Load environment variables
    load_dotenv()
    
    # Get MongoDB connection URL from environment
    mongodb_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
    
    try:
        # Connect to MongoDB
        print(f"Connecting to MongoDB at {mongodb_url}...")
        client = MongoClient(mongodb_url, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.server_info()
        print("Successfully connected to MongoDB!")
        
        # Get database
        db = client.vit_chatbot
        
        # Get all collections
        collections = db.list_collection_names()
        
        if not collections:
            print("No collections found in database.")
            return
        
        # Ask for confirmation
        print("\nThe following collections will be cleared:")
        for collection in collections:
            count = db[collection].count_documents({})
            print(f"- {collection} ({count} documents)")
        
        confirmation = input("\nAre you sure you want to delete all data? (yes/no): ")
        
        if confirmation.lower() != 'yes':
            print("Operation cancelled.")
            return
        
        # Delete all documents from each collection
        for collection in collections:
            result = db[collection].delete_many({})
            print(f"Deleted {result.deleted_count} documents from {collection}")
        
        print("\nDatabase cleanup completed successfully!")
        
    except Exception as e:
        print(f"Error during database cleanup: {e}")
        sys.exit(1)
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    cleanup_database()