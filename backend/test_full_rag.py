import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 1. Load Environment Variables
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CHROMA_DB_DIR = "./data/processed/chroma_db"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")
LLM_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def test_rag_response():
    print("🚀 Testing Full RAG Pipeline (Retrieval + LLM)...")

    # 2. Setup Embeddings & Vector Store
    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=GOOGLE_API_KEY
    )
    
    vector_store = Chroma(
        persist_directory=CHROMA_DB_DIR,
        embedding_function=embeddings
    )
    
    retriever = vector_store.as_retriever(search_kwargs={"k": 2})

    # 3. Setup LLM
    print(f"🤖 Connecting to LLM: {LLM_MODEL}...")
    llm = ChatGoogleGenerativeAI(
        model=LLM_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=0.3
    )

    # 4. Create Prompt Template
    template = """Answer the question based only on the following context:
    {context}

    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    # 5. Create Chain (Modern LCEL Syntax)
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    # 6. Ask a Question
    query = "My computer speed is low when running Docker"
    print(f"\n❓ Question: {query}")
    print("⏳ Thinking...")
    
    try:
        # Invoke the chain
        response = rag_chain.invoke(query)
        
        print("\n✅ LLM Response:")
        print("=" * 60)
        print(response)
        print("=" * 60)
        
        # Manually check sources for debugging
        print("\n📚 Checking Source Documents:")
        docs = retriever.invoke(query)
        for doc in docs:
            print(f"- {doc.metadata.get('source', 'Unknown Source')}")
            
    except Exception as e:
        print(f"\n❌ Error during LLM generation: {e}")

if __name__ == "__main__":
    test_rag_response()