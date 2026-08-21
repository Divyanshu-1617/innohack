# intelligence/routing.py

import networkx as nx

from intelligence.venue_graph import build_venue_graph


class CrowdRouter:

    def __init__(self):
        self.graph = build_venue_graph()

    # --------------------------------------------------
    # 1. Update live crowd information
    # --------------------------------------------------

    def update_crowd(self, crowd_data):
        """
        crowd_data example:

        {
            "Z1": 35,
            "Z2": 120,
            "Z3": 40,
            "S1": 10,
            "S2": 5
        }
        """

        for node, count in crowd_data.items():

            if node in self.graph.nodes:
                self.graph.nodes[node]["people"] = count

    # --------------------------------------------------
    # 2. Calculate crowd density
    # --------------------------------------------------

    def get_density(self, node):

        data = self.graph.nodes[node]

        people = data.get("people", 0)
        capacity = data.get("capacity", 1)

        return people / capacity

    # --------------------------------------------------
    # 3. Crowd status
    # --------------------------------------------------

    def get_status(self, node):

        density = self.get_density(node)

        if density < 0.50:
            return "LOW"

        elif density < 0.75:
            return "MEDIUM"

        elif density < 0.90:
            return "HIGH"

        else:
            return "CRITICAL"

    # --------------------------------------------------
    # 4. Display current venue condition
    # --------------------------------------------------

    def venue_status(self):

        result = {}

        for node, data in self.graph.nodes(data=True):

            if data["type"] in ["zone", "stair"]:

                result[node] = {
                    "people": data.get("people", 0),
                    "capacity": data["capacity"],
                    "density": round(self.get_density(node), 2),
                    "status": self.get_status(node)
                }

        return result

    # --------------------------------------------------
    # 5. Calculate movement cost
    # --------------------------------------------------

    def movement_cost(self, node):

        density = self.get_density(node)

        # Normal movement cost
        if density < 0.50:
            return 1

        elif density < 0.75:
            return 3

        elif density < 0.90:
            return 10

        else:
            # Critical area should strongly discourage routing
            return 1000

    # --------------------------------------------------
    # 6. NORMAL CROWD MANAGEMENT
    # --------------------------------------------------

    def management_recommendation(self):

        recommendations = []

        for node, data in self.graph.nodes(data=True):

            if data["type"] != "zone":
                continue

            status = self.get_status(node)
            density = self.get_density(node)

            if status == "CRITICAL":

                recommendations.append({
                    "zone": node,
                    "action": "STOP_INFLOW",
                    "message": f"{node} is critical. Stop sending additional crowd."
                })

            elif status == "HIGH":

                recommendations.append({
                    "zone": node,
                    "action": "REDUCE_INFLOW",
                    "message": f"{node} is highly crowded. Redirect incoming crowd."
                })

            elif status == "MEDIUM":

                recommendations.append({
                    "zone": node,
                    "action": "MONITOR",
                    "message": f"{node} has moderate crowd. Continue monitoring."
                })

            else:

                recommendations.append({
                    "zone": node,
                    "action": "ACCEPT",
                    "message": f"{node} has available capacity."
                })

        return recommendations

    # --------------------------------------------------
    # 7. Find least crowded neighbouring zone
    # --------------------------------------------------

    def best_neighbour_zone(self, current_zone):

        candidates = []

        for neighbour in self.graph.neighbors(current_zone):

            if self.graph.nodes[neighbour]["type"] != "zone":
                continue

            density = self.get_density(neighbour)

            # Don't recommend nearly full zones
            if density < 0.90:
                candidates.append(
                    (neighbour, density)
                )

        if not candidates:
            return None

        candidates.sort(key=lambda x: x[1])

        return candidates[0][0]

    # --------------------------------------------------
    # 8. Find route between two zones
    # --------------------------------------------------

    def find_route(self, source, destination):

        G = self.graph.copy()

        # Add dynamic weights
        for node in G.nodes:

            if G.nodes[node]["type"] == "exit":
                G.nodes[node]["dynamic_cost"] = 1

            else:
                G.nodes[node]["dynamic_cost"] = self.movement_cost(node)

        # Convert node cost into edge cost
        for u, v in G.edges:

            G.edges[u, v]["weight"] = (
                G.nodes[u]["dynamic_cost"]
                + G.nodes[v]["dynamic_cost"]
            )

        try:

            route = nx.shortest_path(
                G,
                source=source,
                target=destination,
                weight="weight"
            )

            return route

        except nx.NetworkXNoPath:

            return None

    # --------------------------------------------------
    # 9. EXIT ROUTING
    # --------------------------------------------------

    def evacuation_routes(self):

        zones = [
            node
            for node, data in self.graph.nodes(data=True)
            if data["type"] == "zone"
        ]

        exits = [
            node
            for node, data in self.graph.nodes(data=True)
            if data["type"] == "exit"
        ]

        result = {}

        for zone in zones:

            zone_routes = []

            for exit_node in exits:

                route = self.find_route(zone, exit_node)

                if route:

                    # Calculate route congestion
                    congestion = 0

                    for node in route:

                        if self.graph.nodes[node]["type"] != "exit":
                            congestion += self.get_density(node)

                    zone_routes.append({
                        "exit": exit_node,
                        "route": route,
                        "congestion": round(congestion, 2)
                    })

            # Least congested route first
            zone_routes.sort(
                key=lambda x: x["congestion"]
            )

            result[zone] = zone_routes

        return result


# ======================================================
# TEST
# ======================================================

if __name__ == "__main__":

    router = CrowdRouter()

    # Simulated output from your friend's AI
    crowd_data = {
        "Z1": 35,
        "Z2": 120,
        "Z3": 40,
        "S1": 15,
        "S2": 5
    }

    router.update_crowd(crowd_data)

    # --------------------------------------------------
    # NORMAL MANAGEMENT
    # --------------------------------------------------

    print("\n========== VENUE STATUS ==========\n")

    status = router.venue_status()

    for node, data in status.items():

        print(
            f"{node}: "
            f"{data['people']} people | "
            f"{data['density'] * 100:.1f}% | "
            f"{data['status']}"
        )

    print("\n========== MANAGEMENT ==========\n")

    recommendations = router.management_recommendation()

    for recommendation in recommendations:

        print(
            f"{recommendation['zone']} -> "
            f"{recommendation['action']} -> "
            f"{recommendation['message']}"
        )

    # --------------------------------------------------
    # EVACUATION
    # --------------------------------------------------

    print("\n========== EXIT ROUTES ==========\n")

    routes = router.evacuation_routes()

    for zone, zone_routes in routes.items():

        print(f"\n{zone}")

        for route in zone_routes:

            print(
                f"  Exit: {route['exit']} | "
                f"Route: {' -> '.join(route['route'])} | "
                f"Congestion: {route['congestion']}"
            )