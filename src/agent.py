import os
from typing import TypedDict
import operator

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langgraph.graph import StateGraph, START, END

# Define the Agent State
class AgentState(TypedDict):
    question: str
    route: str          # "graph", "vector", or "both"
    graph_context: str  # Context obtained from Neo4j
    vector_context: str # Context obtained from Chroma
    final_answer: str   # Final synthesized answer

def get_graph():
    """Helper to connect to Neo4j."""
    neo4j_url = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.environ.get("NEO4J_USERNAME", "neo4j")
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "password")
    
    # User's specific Aura database name is '93da935a'
    return Neo4jGraph(url=neo4j_url, username=neo4j_user, password=neo4j_password, database="93da935a")

def get_vectorstore():
    """Helper to connect to ChromaDB. Auto-builds from raw_lore.txt on first boot."""
    persist_directory = "data/chroma_db"
    if not os.path.exists(persist_directory) or not os.listdir(persist_directory):
        print("   [VectorDB] ChromaDB not found — building from raw_lore.txt...")
        from src.vector_db import build_vector_db
        build_vector_db()
        print("   [VectorDB] Build complete.")
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    return Chroma(persist_directory=persist_directory, embedding_function=embeddings)

def route_question(state: AgentState):
    """
    Node: Analyzes the question and routes it to the correct retrieval source.
    """
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    prompt = f"""
    You are an AI router for an Attack on Titan knowledge base.
    Decide whether the user's question requires:
    - 'graph': for relational questions (e.g., Who inherited?, Who is allied with?, Who killed?).
    - 'vector': for descriptive/semantic questions (e.g., Describe the layout, What does the titan look like?).
    - 'both': if it asks for both relations and descriptions, or if it's ambiguous.
    
    Question: {state['question']}
    
    Respond with exactly one word: graph, vector, or both.
    """
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        route = response.content.strip().lower()
        if route not in ["graph", "vector", "both"]:
            route = "both" # fallback to both if model hallucinates
    except Exception as e:
        print(f"Routing error fallback applied. {e}")
        route = "both"
        
    print(f"   [Router] Directing question to: {route}")
    return {"route": route}

def retrieve_graph(state: AgentState):
    """
    Node: Retrieves relational data from Neo4j using GraphCypherQAChain.
    """
    print("   [Retriever] Querying Knowledge Graph...")
    if state["route"] in ["graph", "both"]:
        try:
            graph = get_graph()
            llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
            
            # Use allow_dangerous_requests=True intentionally as we own the database locally
            chain = GraphCypherQAChain.from_llm(
                graph=graph, 
                llm=llm, 
                verbose=False,
                allow_dangerous_requests=True 
            )
            result = chain.invoke({"query": state["question"]})
            context = result.get("result", "")
            return {"graph_context": f"Graph Results:\n{context}"}
        except Exception as e:
            return {"graph_context": f"Note: Graph Retrieval Error/Unavailable. {e}"}
            
    return {"graph_context": ""}

def retrieve_vector(state: AgentState):
    """
    Node: Retrieves descriptive data from ChromaDB via similarity search.
    """
    print("   [Retriever] Querying Vector Database...")
    if state["route"] in ["vector", "both"]:
        try:
            vectorstore = get_vectorstore()
            docs = vectorstore.similarity_search(state["question"], k=3)
            context = "\n".join([f"- {doc.page_content}" for doc in docs])
            return {"vector_context": f"Vector Results:\n{context}"}
        except Exception as e:
            return {"vector_context": f"Note: Vector Retrieval Error/Unavailable. {e}"}
            
    return {"vector_context": ""}

def generate_answer(state: AgentState):
    """
    Node: Combines context and synthesizes the final response.
    """
    print("   [Generator] Formulating final response...")
    llm = ChatGroq(model="llama-3.1-8b-instant")
    
    system_prompt = """You are an expert on Attack on Titan lore. 
    Provide a comprehensive answer to the user's question using ONLY the provided context.
    If the context contains conflicting information, use your best judgment synthesizing it.
    If you don't know the answer strictly based on the context, state that clearly instead of hallucinating.
    Structure your answer cleanly using clear markdown formatting.
    """
    
    user_prompt = f"User Question: {state['question']}\n\n"
    if state["graph_context"]:
        user_prompt += f"{state['graph_context']}\n\n"
    if state["vector_context"]:
        user_prompt += f"{state['vector_context']}\n\n"
        
    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        final_answer = response.content
    except Exception as e:
        final_answer = f"Error during generation: {e}"
    
    return {"final_answer": final_answer}

def determine_next_steps(state: AgentState):
    """
    Conditional logic determining which path(s) to take after routing.
    """
    route = state.get("route", "both")
    if route == "graph":
        return ["retrieve_graph"]
    elif route == "vector":
        return ["retrieve_vector"]
    else:
        # Fork to both retrieve nodes
        return ["retrieve_graph", "retrieve_vector"]

def build_graph_agent():
    """
    Compiles the langgraph workflow and returns the agent app.
    """
    workflow = StateGraph(AgentState)
    
    # Add nodes to graph
    workflow.add_node("route_question", route_question)
    workflow.add_node("retrieve_graph", retrieve_graph)
    workflow.add_node("retrieve_vector", retrieve_vector)
    workflow.add_node("generate_answer", generate_answer)
    
    # Establish connections
    workflow.add_edge(START, "route_question")
    
    # Conditional branching for parallel or distinct retrievals
    workflow.add_conditional_edges(
        "route_question",
        determine_next_steps,
        {
            "retrieve_graph": "retrieve_graph",
            "retrieve_vector": "retrieve_vector"
        }
    )
    
    # Join point: generation requires both retrieval paths to finish
    workflow.add_edge("retrieve_graph", "generate_answer")
    workflow.add_edge("retrieve_vector", "generate_answer")
    
    # End edge
    workflow.add_edge("generate_answer", END)
    
    # Return compiled app
    return workflow.compile()
