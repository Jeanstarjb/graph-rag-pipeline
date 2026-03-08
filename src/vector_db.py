import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

def build_vector_db():
    """
    Reads the scraped text, creates embeddings using a HuggingFace model,
    and stores them in a local Chroma vector database.
    """
    raw_lore_path = "data/raw_lore.txt"
    if not os.path.exists(raw_lore_path):
        print(f"Error: {raw_lore_path} not found. Please run the scraper first.")
        return
        
    with open(raw_lore_path, "r", encoding="utf-8") as f:
        text = f.read()
        
    print("Splitting text into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.create_documents([text])
    
    print(f"Created {len(docs)} document chunks.")
    
    print("Initializing HuggingFace embeddings (Model: BAAI/bge-small-en-v1.5)...")
    # This will download the model weights locally if not already present
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    
    persist_directory = "data/chroma_db"
    print(f"Upserting to ChromaDB at '{persist_directory}'...")
    
    # Store documents in the ChromaDB vectorstore
    vectorstore = Chroma.from_documents(
        documents=docs, 
        embedding=embeddings, 
        persist_directory=persist_directory
    )
    
    print("Vector database built successfully!")

if __name__ == "__main__":
    build_vector_db()
