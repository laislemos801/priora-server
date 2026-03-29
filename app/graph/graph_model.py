import networkx as nx

def build_graph():
    G = nx.Graph()
    G.add_edge("Suspect A", "Evidence 1")
    return G