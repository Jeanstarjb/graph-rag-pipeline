import os
from pyvis.network import Network
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

def generate_graph_html():
    """
    Connects to Neo4j, retrieves a sample of the knowledge graph, and uses PyVis
    to generate an interactive dark-themed HTML string (no file I/O — works on cloud).
    """
    net = Network(
        height="600px",
        width="100%",
        bgcolor="#0a0a0a",
        font_color="white",
        directed=True,
    )
    net.force_atlas_2based()

    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

        with driver.session(database="93da935a") as session:
            query = "MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 150"
            result = session.run(query)

            added_nodes = set()

            for record in result:
                node_n = record["n"]
                node_m = record["m"]
                rel_r = record["r"]

                label_n = list(node_n.labels)[0] if node_n.labels else "Unknown"
                label_m = list(node_m.labels)[0] if node_m.labels else "Unknown"

                id_n = node_n.element_id
                id_m = node_m.element_id

                name_n = node_n.get("id", str(id_n))
                name_m = node_m.get("id", str(id_m))

                def get_color(label):
                    label_clean = label.lower()
                    if "character" in label_clean or "person" in label_clean:
                        return "#dc2626"   # Crimson — People
                    elif "faction" in label_clean or "organization" in label_clean:
                        return "#16a34a"   # Green — Factions
                    elif "location" in label_clean or "place" in label_clean:
                        return "#2563eb"   # Blue — Locations
                    elif "titan" in label_clean:
                        return "#f59e0b"   # Amber — Titans
                    elif "event" in label_clean:
                        return "#8b5cf6"   # Purple — Events
                    return "#6b7280"       # Gray — Concepts / Other

                color_n = get_color(label_n)
                color_m = get_color(label_m)

                if id_n not in added_nodes:
                    net.add_node(id_n, label=name_n, color=color_n, title=f"Type: {label_n}")
                    added_nodes.add(id_n)

                if id_m not in added_nodes:
                    net.add_node(id_m, label=name_m, color=color_m, title=f"Type: {label_m}")
                    added_nodes.add(id_m)

                rel_type = rel_r.type
                net.add_edge(id_n, id_m, title=rel_type, label=rel_type, color="#4ade80")

        driver.close()

    except Exception as e:
        print(f"Error generating graph from Neo4j: {e}")
        net.add_node("error", label="Error connecting to Neo4j", color="#ff0000")

    # Return HTML string directly — no disk write needed (safe for Streamlit Cloud)
    try:
        return net.generate_html(notebook=False)
    except Exception as e:
        print(f"Error generating PyVis HTML: {e}")
        return ""


if __name__ == "__main__":
    print("Generating Knowledge Graph...")
    html = generate_graph_html()
    if html:
        print(f"Success! Generated {len(html)} bytes of HTML.")
    else:
        print("Failed to generate graph.")
