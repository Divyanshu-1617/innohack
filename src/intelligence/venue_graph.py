# intelligence/venue_graph.py

import networkx as nx


def build_venue_graph():
    """
    Venue layout:

                    FRONT
             GATE_L       GATE_R
                |           |
                Z1          Z3
                 \          /
                  S1      S2
                    \    /
                       Z2

    The graph can be modified later according to the actual venue.
    """

    G = nx.Graph()

    # -------------------------
    # Zones
    # -------------------------
    G.add_node("Z1", type="zone", capacity=100)
    G.add_node("Z2", type="zone", capacity=150)
    G.add_node("Z3", type="zone", capacity=100)

    # -------------------------
    # Stairs / movement points
    # -------------------------
    G.add_node("S1", type="stair", capacity=40)
    G.add_node("S2", type="stair", capacity=40)

    # -------------------------
    # Exits
    # -------------------------
    G.add_node("GATE_L", type="exit", capacity=150)
    G.add_node("GATE_R", type="exit", capacity=150)

    # -------------------------
    # Connections
    # -------------------------

    # Left side
    G.add_edge("Z1", "S1", distance=1)
    G.add_edge("S1", "GATE_L", distance=1)

    # Centre
    G.add_edge("Z2", "S1", distance=1)
    G.add_edge("Z2", "S2", distance=1)

    # Right side
    G.add_edge("Z3", "S2", distance=1)
    G.add_edge("S2", "GATE_R", distance=1)

    return G


if __name__ == "__main__":
    graph = build_venue_graph()

    print("Venue Nodes:")
    for node, data in graph.nodes(data=True):
        print(node, data)

    print("\nVenue Connections:")
    for u, v, data in graph.edges(data=True):
        print(u, "<->", v, data)