import os
import sys
from dotenv import load_dotenv

# Ensure the local 'src' directory can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.scraper import scrape_wiki
from src.knowledge_graph import build_knowledge_graph
from src.vector_db import build_vector_db
from src.agent import build_graph_agent

def verify_env_vars():
    """Check if necessary environment variables are set."""
    load_dotenv()
    missing = []
    if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("GITHUB_TOKEN"):
        missing.append("OPENAI_API_KEY or GITHUB_TOKEN")
    if not os.environ.get("NEO4J_URI"):
        missing.append("NEO4J_URI")
    if not os.environ.get("NEO4J_USERNAME"):
        missing.append("NEO4J_USERNAME")
    if not os.environ.get("NEO4J_PASSWORD"):
        missing.append("NEO4J_PASSWORD")
        
    if missing:
        print("\n" + "!"*50)
        print("WARNING: Missing environment variables:")
        for m in missing:
            print(f"  - {m}")
        print("Please create or update your .env file before running DB build or the agent.")
        print("!"*50 + "\n")
    return not missing

def display_menu():
    print("\n" + "="*50)
    print("HYBRID GRAPHRAG COMMANDER (ATTACK ON TITAN LORE)")
    print("="*50)
    print("1. Run the Scraper (Harvest Lore)")
    print("2. Build the Databases (Neo4j & ChromaDB)")
    print("3. Chat with the Hybrid GraphRAG Agent")
    print("4. Exit")
    print("="*50)

def main():
    verify_env_vars()
    
    while True:
        display_menu()
        choice = input("Select an option (1-4): ").strip()
        
        if choice == "1":
            print("\n" + "-"*30)
            print("Running Scraper")
            print("-"*30)
            scrape_wiki()
            
        elif choice == "2":
            print("\n" + "-"*30)
            print("Building Databases")
            print("-"*30)
            
            print("\n--- 1/2: Building Vector Database (Chroma) ---")
            build_vector_db()
            
            print("\n--- 2/2: Building Knowledge Graph (Neo4j) ---")
            build_knowledge_graph()
            
            print("\n>>> Database builds completed!")
            
        elif choice == "3":
            print("\n" + "-"*30)
            print("Starting Hybrid GraphRAG Agent")
            print("-"*30)
            print("Type 'exit' or 'quit' to return to menu.")
            
            try:
                app = build_graph_agent()
                
                while True:
                    user_input = input("\n[Query] >> ")
                    if user_input.lower() in ['exit', 'quit']:
                        break
                    if not user_input.strip():
                        continue
                        
                    print("\nProcessing...")
                    # Initialize our state
                    initial_state = {
                        "question": user_input, 
                        "route": "", 
                        "graph_context": "", 
                        "vector_context": "", 
                        "final_answer": ""
                    }
                    
                    # Invoke langgraph application
                    result = app.invoke(initial_state)
                    
                    print("\n" + "="*40)
                    print("FINAL ANSWER")
                    print("="*40)
                    print(result.get("final_answer", "No answer generated."))
                    print("="*40)
                    
            except Exception as e:
                print(f"Error initializing or running agent: {e}")
                
        elif choice == "4":
            print("Exiting Commander. Goodbye!")
            sys.exit(0)
            
        else:
            print("Invalid choice. Please select from 1-4.")

if __name__ == "__main__":
    main()
