import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_community.graphs import Neo4jGraph
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

def build_knowledge_graph():
    """
    Processes the raw lore text and pushes nodes/edges to Neo4j database.
    Required .env vars: NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, GROQ_API_KEY
    """
    neo4j_url = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.environ.get("NEO4J_USERNAME", "neo4j")
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "password")
    
    # Check if API key is present
    if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("GITHUB_TOKEN"):
        print("Error: Required API key (OPENAI_API_KEY or GITHUB_TOKEN) environment variable is not set. Please set it in .env file.")
        return

    print("Connecting to Neo4j...")
    try:
        # User's specific Aura database name is '93da935a'
        graph = Neo4jGraph(url=neo4j_url, username=neo4j_user, password=neo4j_password, database="93da935a")
    except Exception as e:
        print(f"Failed to connect to Neo4j: {e}")
        print("Make sure your Neo4j database is running and credentials are correct.")
        return
    
    raw_lore_path = "data/raw_lore.txt"
    if not os.path.exists(raw_lore_path):
        print(f"Error: {raw_lore_path} not found. Please run the scraper first.")
        return
        
    with open(raw_lore_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Split text. LLMGraphTransformer can exceed token limits if the chunk is too massive
    print("Splitting text into smaller chunks for the model...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_text(text)
    
    # To avoid exhausting rate limits and time, we'll process a subset if needed, 
    # but for this script we will process all chunks.
    documents = [Document(page_content=chunk) for chunk in chunks]
    print(f"Generated {len(documents)} chunks to process.")
    
    print("Initializing GitHub Models LLM...")
    from langchain_openai import ChatOpenAI
    # Point the OpenAI client to the GitHub Models Azure endpoint
    llm = ChatOpenAI(
        model="gpt-4o-mini", 
        temperature=0,
        api_key=os.environ.get("GITHUB_TOKEN", os.environ.get("OPENAI_API_KEY")),
        base_url="https://models.inference.ai.azure.com"
    )
    
    # Constrain the schema so the model doesn't hallucinate the JSON format
    allowed_nodes = ["Person", "Titan", "Location", "Faction", "Event", "Concept"]
    allowed_relationships = ["KILLED", "ALLIED_WITH", "POSSESSES", "LOCATED_IN", "PART_OF", "PARTICIPATED_IN"]
    
    llm_transformer = LLMGraphTransformer(
        llm=llm,
        allowed_nodes=allowed_nodes,
        allowed_relationships=allowed_relationships
    )
    
    print(f"Extracting graph documents. This might take a moment based on text size...")
    try:
        # Note: If rate limits apply, you might need to process these in batches
        graph_documents = llm_transformer.convert_to_graph_documents(documents)
        print(f"Extracted {len(graph_documents)} graph documents.")
        
        print("Pushing to Neo4j...")
        graph.add_graph_documents(graph_documents, include_source=True)
        print("Knowledge graph built successfully!")
    except Exception as e:
        print(f"An error occurred during graph processing: {e}")

if __name__ == "__main__":
    build_knowledge_graph()
