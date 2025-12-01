import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

# Get the absolute path of the backend directory
BACKEND_DIR = Path(__file__).resolve().parent
DATA_DIR = BACKEND_DIR / "data" / "processed"
ENV_PATH = BACKEND_DIR / ".env"

# Load Environment Variables
load_dotenv(ENV_PATH)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# Force the path to be absolute based on the script location
CHROMA_DB_DIR = DATA_DIR / "chroma_db"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")

def test_retrieval():
    print(f"📂 Working Directory: {os.getcwd()}")
    print(f"📂 Script Directory:  {BACKEND_DIR}")
    print(f"📂 Looking for DB at: {CHROMA_DB_DIR}")

    print("\n--- 1. Testing Embeddings Configuration ---")
    if not GOOGLE_API_KEY:
        print("❌ Error: GOOGLE_API_KEY not found in .env")
        return

    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=GOOGLE_API_KEY
    )
    print(f"✅ Embeddings initialized with model: {EMBEDDING_MODEL}")

    print("\n--- 2. Connecting to Vector Database ---")
    if not CHROMA_DB_DIR.exists():
        print(f"❌ Error: Database directory does not exist at: {CHROMA_DB_DIR}")
        print("   Contents of parent folder:")
        if DATA_DIR.exists():
            for item in DATA_DIR.iterdir():
                print(f"   - {item.name}")
        else:
            print(f"   Parent folder {DATA_DIR} does not exist either.")
        return

    # Check if it looks like a valid ChromaDB
    if not (CHROMA_DB_DIR / "chroma.sqlite3").exists():
        print("⚠️  WARNING: 'chroma.sqlite3' not found inside chroma_db folder.")
        print("   This might be an empty folder or the wrong version of Chroma.")

    vector_store = Chroma(
        persist_directory=str(CHROMA_DB_DIR),
        embedding_function=embeddings
    )
    
    # Check if DB is empty
    try:
        # Note: _collection is internal, but useful for debugging
        count = vector_store._collection.count()
        print(f"✅ Database connected. Total documents: {count}")
        if count == 0:
            print("⚠️  WARNING: Database is empty! You need to ingest data first.")
            return
    except Exception as e:
        print(f"❌ Error accessing collection: {e}")
        return

    print("\n--- 3. Testing Similarity Search ---")
    query = "my computer speed is low"
    print(f"🔎 Query: '{query}'")
    
    # Perform search
    results = vector_store.similarity_search_with_score(query, k=3)
    
    if not results:
        print("❌ No results found. The embedding search failed.")
    else:
        print(f"✅ Found {len(results)} relevant documents:\n")
        for i, (doc, score) in enumerate(results):
            print(f"   [Result {i+1}] (Score: {score:.4f})") 
            print(f"   Content: {doc.page_content[:200]}...") 
            print(f"   Source: {doc.metadata.get('source', 'Unknown')}")
            print("-" * 50)

if __name__ == "__main__":
    test_retrieval()