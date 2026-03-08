import streamlit as st
import sys
import os
import time
import base64

# Ensure src/ is importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Survey Corps Intelligence Archive",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Helper: Load Image as Base64 ──────────────────────────────────────────────
@st.cache_data
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Try to load the background image
bg_img_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "peakpx.jpg")
bg_css = ""
if os.path.exists(bg_img_path):
    bin_str = get_base64_of_bin_file(bg_img_path)
    bg_css = f"""
    .stApp {{
        background-image: url("data:image/jpeg;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    """
else:
    bg_css = """
    .stApp {{
        background-color: #0a0a0a;
    }}
    """

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
    /* Import military-grade monospace font */
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');

    /* Global Typography */
    .stApp {{
        font-family: 'Rajdhani', sans-serif;
    }}

    /* Global text colors — forcing bright white with shadow for visibility against complex backgrounds */
    .stMarkdown, .stText, p, span, li {{
        color: #ffffff !important;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.9), 2px 2px 5px rgba(0, 0, 0, 0.7) !important;
    }}

    /* Inject the Dynamic Background */
    {bg_css}

    /* Remove the heavy dark box / glassmorphism block from main content */
    [data-testid="stMainBlockContainer"] {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        backdrop-filter: none !important;
        -webkit-backdrop-filter: none !important;
        padding-top: 2rem !important;
    }}

    /* Main header */
    h1 {{
        font-family: 'Rajdhani', sans-serif !important;
        color: #ff4444 !important;
        text-shadow: 0 0 10px rgba(0, 0, 0, 1), 0 0 20px rgba(139, 0, 0, 0.8) !important;
        letter-spacing: 0.1em;
        border-bottom: 2px solid rgba(255, 68, 68, 0.6);
        padding-bottom: 0.5rem;
    }}

    /* Headers / Subheaders */
    h2, h3, h4, h5, h6 {{
        color: #ffffff !important;
        text-shadow: 1px 1px 4px rgba(0, 0, 0, 1) !important;
    }}

    /* Sidebar - keeping it slightly dark to divide it, but much cleaner */
    [data-testid="stSidebar"] {{
        background: rgba(10, 10, 10, 0.8) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {{
        color: #4ade80 !important;
        font-family: 'Share Tech Mono', monospace !important;
        letter-spacing: 0.05em;
    }}
    
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] div {{
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 0.85rem;
    }}

    /* Success indicators on sidebar */
    .stAlert {{
        background-color: transparent !important;
        border: 1px solid #4ade80 !important;
        border-radius: 4px !important;
        font-family: 'Share Tech Mono', monospace !important;
        color: #4ade80 !important;
        box-shadow: 0 0 8px rgba(74, 222, 128, 0.2);
    }}

    /* Chat messages — clear the dark boxes completely for a true terminal look directly over image */
    [data-testid="stChatMessage"] {{
        background: transparent !important;
        border: none !important;
        backdrop-filter: none !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 1rem 0;
    }}

    /* Chat input styling */
    [data-testid="stChatInput"] {{
        background: transparent !important;
        padding: 0;
    }}
    /* Force inner wrappers to be transparent so white corners don't peek out */
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] > div > div {{
        background: transparent !important;
        border: none !important;
    }}
    [data-testid="stChatInput"] textarea {{
        background-color: rgba(0, 0, 0, 0.7) !important;
        border: 1px solid rgba(255, 68, 68, 0.8) !important;
        color: #ffffff !important;
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 1rem !important;
        text-shadow: none !important;
        border-radius: 8px !important;
        padding-left: 1rem !important;
    }}
    [data-testid="stChatInput"] textarea:focus {{
        border: 1px solid #ff4444 !important;
        box-shadow: 0 0 10px rgba(255, 68, 68, 0.5) !important;
    }}
    /* Make the send icon visible */
    [data-testid="stChatInput"] button {{
        background: transparent !important;
        color: #ff4444 !important;
    }}
    [data-testid="stChatInput"] button:hover {{
        color: #ff8888 !important;
    }}

    /* Code blocks inside answers */
    code, pre {{
        background: rgba(0, 0, 0, 0.8) !important;
        color: #4ade80 !important;
        font-family: 'Share Tech Mono', monospace !important;
        border: 1px solid rgba(22, 163, 74, 0.3);
        border-radius: 4px;
        text-shadow: none !important;
    }}

    /* Spinner text */
    .stSpinner > div {{
        color: #4ade80;
        font-family: 'Share Tech Mono', monospace;
        font-weight: bold;
        text-shadow: 1px 1px 3px rgba(0,0,0,1);
    }}

    /* The route badge */
    .route-badge {{
        display: inline-block;
        padding: 3px 10px;
        border-radius: 4px;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 8px;
        letter-spacing: 0.05em;
        text-shadow: none !important;
    }}
    .route-graph {{
        background-color: rgba(0, 0, 0, 0.8);
        color: #a78bfa;
        border: 1px solid #8b5cf6;
    }}
    .route-vector {{
        background-color: rgba(0, 0, 0, 0.8);
        color: #4ade80;
        border: 1px solid #22c55e;
    }}
    .route-both {{
        background-color: rgba(0, 0, 0, 0.8);
        color: #fde047;
        border: 1px solid #eab308;
    }}
</style>
""", unsafe_allow_html=True)

# ── Agent loader (cached so we only build the graph once) ─────────────────────
@st.cache_resource(show_spinner="Initializing LangGraph agent... Stand by.")
def load_agent():
    try:
        from src.agent import build_graph_agent
        return build_graph_agent()
    except Exception as e:
        st.error(f"Failed to load agent: {e}")
        return None

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("# 🖥 C.L.E. TERMINAL")
    st.markdown("---")
    st.markdown(
        """
        **SYSTEM BRIEF**  
        This terminal interfaces with a dual-source intelligence archive:
        
        - **Neo4j Knowledge Graph** — Structured entity relationships (who killed who, factions, alliances).  
        - **ChromaDB Vector Store** — Semantic lore fragments (descriptions, events, history).
        
        The LangGraph routing agent automatically selects the optimal retrieval path(s) per query.
        """,
    )
    st.markdown("---")
    st.markdown("**🔗 UPLINK STATUS**")
    st.success("⬤  Neo4j Link: ACTIVE")
    st.success("⬤  ChromaDB: MOUNTED")
    st.success("⬤  Groq LLM: ONLINE")
    st.success("⬤  HuggingFace Embeddings: LOADED")
    st.markdown("---")
    st.markdown("**📁 INTEL SOURCES**")
    st.markdown(
        """
        ```
        Wiki: attackontitan.fandom.com  
        Scope: Eren Yeager, Survey Corps,
               Marley, Titans, Historia…
        Chunks: 49 indexed fragments
        Graph : 49 extracted documents
        ```
        """
    )
    st.markdown("---")
    st.caption("⚠️  Classified Level: OMEGA\n\nUnauthorized access will be reported to Captain Levi.")

    if st.button("🗑️  Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Main Header ───────────────────────────────────────────────────────────────
st.markdown("# ⚔️ Survey Corps Intelligence Archive")
st.markdown(
    "<p style='color:#a0a0a0; font-family:Share Tech Mono, monospace; font-size:0.9rem; letter-spacing: 0.05em;'>"
    "HYBRID GRAPHRAG SYSTEM v1.0 · NEO4J + CHROMADB · GROQ INFERENCE ENGINE</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ── Session State Init ────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "**SYSTEM ONLINE.** Welcome, Commander.\n\n"
                "You are connected to the Survey Corps Intelligence Archive. "
                "This terminal queries a hybrid knowledge system — structured relationship graphs "
                "and semantic vector memory — to answer your questions about Attack on Titan lore.\n\n"
                "**Example queries:**\n"
                "- *Who is Eren Yeager allied with?*\n"
                "- *What happened during the fall of Shiganshina?*\n"
                "- *What is the Founding Titan's power?*\n"
                "- *Who are the Nine Titans?*"
            ),
            "route": None,
        }
    ]

# ── Render Chat History ───────────────────────────────────────────────────────
for msg in st.session_state.messages:
    avatar = "🪖" if msg["role"] == "user" else "⚔️"
    with st.chat_message(msg["role"], avatar=avatar):
        # Show route badge if available
        if msg.get("route"):
            route = msg["route"]
            badge_class = {
                "graph": "route-graph",
                "vector": "route-vector",
                "both": "route-both",
            }.get(route, "route-both")
            label = {
                "graph": "📡 KNOWLEDGE GRAPH",
                "vector": "🧠 VECTOR SEARCH",
                "both": "⚡ HYBRID RETRIEVAL",
            }.get(route, "⚡ HYBRID RETRIEVAL")
            st.markdown(
                f'<span class="route-badge {badge_class}">{label}</span>',
                unsafe_allow_html=True,
            )
        st.markdown(msg["content"])

# ── Chat Input ────────────────────────────────────────────────────────────────
query = st.chat_input("Enter query, Commander...")

if query:
    # 1. Append and display user message
    st.session_state.messages.append({"role": "user", "content": query, "route": None})
    with st.chat_message("user", avatar="🪖"):
        st.markdown(query)

    # 2. Run the agent with a spinner
    with st.chat_message("assistant", avatar="⚔️"):
        with st.spinner("Accessing the Paths..."):
            try:
                app = load_agent()
                if app is None:
                    raise ValueError("Agent failed to initialize. Check your database configurations.")
                
                initial_state = {
                    "question": query,
                    "route": "",
                    "graph_context": "",
                    "vector_context": "",
                    "final_answer": "",
                }
                result = app.invoke(initial_state)
                route = result.get("route", "both")
                answer = result.get("final_answer", "No answer was generated.")
            except Exception as e:
                route = "both"
                answer = f"⚠️ **System Error:** `{e}`\n\nPlease verify your `.env` credentials and database connections."

        # 3. Show route badge
        badge_class = {
            "graph": "route-graph",
            "vector": "route-vector",
            "both": "route-both",
        }.get(route, "route-both")
        label = {
            "graph": "📡 KNOWLEDGE GRAPH",
            "vector": "🧠 VECTOR SEARCH",
            "both": "⚡ HYBRID RETRIEVAL",
        }.get(route, "⚡ HYBRID RETRIEVAL")
        st.markdown(
            f'<span class="route-badge {badge_class}">{label}</span>',
            unsafe_allow_html=True,
        )

        # 4. Stream the response character by character for terminal effect
        placeholder = st.empty()
        displayed = ""
        for char in answer:
            displayed += char
            placeholder.markdown(displayed + "▌")
            time.sleep(0.004)
        placeholder.markdown(displayed)

    # 5. Save to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "route": route,
    })
