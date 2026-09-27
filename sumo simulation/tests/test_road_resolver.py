import os
import unittest
import numpy as np
import networkx as nx

from backend.graph.road_resolver import RoadMetadataResolver
from backend.graph.dynamic_graph import DynamicTrafficGraph
from backend.vrp.problem_instance import ProblemInstance, VehicleConfig, Order
from backend.vrp.vrp_evaluator import VRPEvaluator
from backend.routing.dijkstra_router import DijkstraRouter
from backend.routing.astar_router import AStarRouter
from backend.vrp.dijkstra_vrp import DijkstraVRPSolver
from backend.vrp.qpso_vrp import QPSOVRPSolver
from backend.vrp.qaoa_vrp import QAOAVRPSolver
from backend.vrp.alns_vrp import ALNSVRPSolver
from backend.vrp.hgs_vrp import HGSVRPSolver
from backend.vrp.exact_mip_vrp import ExactMIPVRPSolver
from backend.vrp.rerouter import DynamicRerouter
from backend.vrp.experiment_db import ExperimentDatabase


def build_named_test_graph():
    """Constructs a test graph with named roads, unnamed roads, and internal junction connectors."""
    dt = DynamicTrafficGraph()
    positions = {
        'n0': (0.0, 0.0),
        'n1': (100.0, 0.0),
        'n2': (200.0, 0.0),
        'n3': (0.0, 100.0),
        'n4': (100.0, 100.0),
        'n5': (200.0, 100.0),
    }
    for nid, pos in positions.items():
        dt.node_positions[nid] = pos
        dt.graph.add_node(nid)

    # Edge definitions: (u, v, eid, length, speed, road_name)
    edges = [
        ('n0', 'n1', 'e01', 100.0, 10.0, 'Shivaji Road'),
        ('n1', 'n0', 'e10', 100.0, 10.0, 'Shivaji Road'),
        ('n1', 'n2', 'e12', 100.0, 10.0, 'Shivaji Road'),  # Continuation of Shivaji Road
        ('n2', 'n1', 'e21', 100.0, 10.0, 'Shivaji Road'),
        ('n0', 'n3', 'e03', 100.0, 10.0, 'Jangali Maharaj Road'),
        ('n3', 'n0', 'e30', 100.0, 10.0, 'Jangali Maharaj Road'),
        ('n1', 'n4', 'e14', 100.0, 10.0, 'FC Road'),
        ('n4', 'n1', 'e41', 100.0, 10.0, 'FC Road'),
        ('n2', 'n5', 'e25', 100.0, 10.0, ''),  # Unnamed road
        ('n5', 'n2', 'e52', 100.0, 10.0, ''),  # Unnamed road
        ('n3', 'n4', 'e34', 100.0, 10.0, 'Karve Road'),
        ('n4', 'n3', 'e43', 100.0, 10.0, 'Karve Road'),
        ('n4', 'n5', 'e45', 100.0, 10.0, 'Karve Road'),
        ('n5', 'n4', 'e54', 100.0, 10.0, 'Karve Road'),
        ('n1', 'n4', ':j1_0', 10.0, 5.0, ''),  # Internal connector
    ]

    edge_name_map = {}
    for u, v, eid, length, speed, rname in edges:
        dt.graph.add_edge(u, v, weight=length / speed, length=length, speed_limit=speed, edge_id=eid)
        dt.edge_metadata[eid] = {
            'edge_id': eid,
            'road_name': rname,
            'from_node': u,
            'to_node': v,
            'length': length,
            'speed_limit': speed,
            'lane_count': 1,
            'mean_speed': speed,
            'vehicle_count': 0,
            'congestion_ratio': 0.0,
            'travel_time': length / speed,
            'shape': [(positions[u][0], positions[u][1]), (positions[v][0], positions[v][1])],
        }
        if rname:
            edge_name_map[eid] = rname

    dt.road_resolver.load_from_dict(edge_name_map)
    return dt


class TestRoadResolver(unittest.TestCase):
    def setUp(self):
        self.dt = build_named_test_graph()
        self.resolver = self.dt.road_resolver

        self.vehicles = [
            VehicleConfig(vehicle_id="V1", capacity=30.0, start_node="n0", color="#3b82f6"),
            VehicleConfig(vehicle_id="V2", capacity=30.0, start_node="n0", color="#10b981"),
        ]
        self.problem = ProblemInstance(
            origin="n0",
            destinations=["n2", "n5"],
            graph=self.dt,
            num_vehicles=2,
            vehicles=self.vehicles,
            customer_demands={"n2": 10.0, "n5": 10.0},
        )

    def test_requirement_a_edge_metadata_extraction(self):
        """A. Named edges have non-empty street names; unnamed edges fall back gracefully."""
        # Named edge
        meta_named = self.resolver.resolve_edge("e01")
        self.assertEqual(meta_named.road_name, "Shivaji Road")
        self.assertEqual(meta_named.edge_id, "e01")
        self.assertFalse(meta_named.is_internal)

        # Unnamed edge
        meta_unnamed = self.resolver.resolve_edge("e25")
        self.assertEqual(meta_unnamed.road_name, "Unnamed road")
        self.assertFalse(meta_unnamed.is_internal)

    def test_requirement_b_internal_junction_edges(self):
        """B. Junction/internal edges (starting with ':') resolve to 'Internal connector' and is_internal=True."""
        meta_internal = self.resolver.resolve_edge(":j1_0")
        self.assertEqual(meta_internal.road_name, "Internal connector")
        self.assertTrue(meta_internal.is_internal)

        meta_internal_arbitrary = self.resolver.resolve_edge(":junction_cluster_44_2")
        self.assertEqual(meta_internal_arbitrary.road_name, "Internal connector")
        self.assertTrue(meta_internal_arbitrary.is_internal)

    def test_requirement_c_deterministic_fallback(self):
        """C. Deterministic fallback: Unknown edge IDs resolve to 'Unnamed road'."""
        unknown_name = self.resolver.get_road_name("non_existent_edge_9999")
        self.assertEqual(unknown_name, "Unnamed road")

        unknown_meta = self.resolver.resolve_edge("completely_bogus_edge")
        self.assertEqual(unknown_meta.road_name, "Unnamed road")
        self.assertEqual(unknown_meta.edge_id, "completely_bogus_edge")
        self.assertFalse(unknown_meta.is_internal)

    def test_requirement_d_1_to_1_alignment(self):
        """D. 1-to-1 alignment: len(road_path) == len(edge_path) for any resolved route."""
        edge_path = ["e01", "e12", ":j1_0", "e25", "unknown_edge"]
        road_path, display_route, route_steps = self.resolver.resolve_edge_path(edge_path)

        self.assertEqual(len(road_path), len(edge_path))
        self.assertEqual(len(route_steps), len(edge_path))

        # Check each step corresponds to edge
        for idx, edge_id in enumerate(edge_path):
            self.assertEqual(route_steps[idx]["edge_id"], edge_id)
            self.assertEqual(route_steps[idx]["road_name"], road_path[idx])

    def test_requirement_e_consecutive_deduplication(self):
        """E. Consecutive deduplication: compress_road_sequence(['A', 'A', 'B', 'B', 'A']) == ['A', 'B', 'A']."""
        compressed = self.resolver.compress_road_sequence(["A", "A", "B", "B", "A"])
        self.assertEqual(compressed, ["A", "B", "A"])

        # Also test with real road names
        roads = ["Shivaji Road", "Shivaji Road", "Karve Road", "Karve Road", "FC Road"]
        self.assertEqual(
            self.resolver.compress_road_sequence(roads),
            ["Shivaji Road", "Karve Road", "FC Road"]
        )

        # Single element and empty list
        self.assertEqual(self.resolver.compress_road_sequence(["Solo"]), ["Solo"])
        self.assertEqual(self.resolver.compress_road_sequence([]), [])

    def test_requirement_f_all_algorithms_produce_road_names(self):
        """F. Every solver returns non-empty road_path and display_route on a test problem instance."""
        # 1. Dijkstra Shortest Path Router
        dijk_router = DijkstraRouter()
        res_dijk_router = dijk_router.find_shortest_path(self.dt, "n0", "n2")
        self.assertTrue(len(res_dijk_router["road_path"]) > 0)
        self.assertTrue(len(res_dijk_router["display_route"]) > 0)
        self.assertEqual(len(res_dijk_router["road_path"]), len(res_dijk_router["edge_path"]))

        # 2. A* Router
        astar_router = AStarRouter()
        res_astar = astar_router.find_shortest_path(self.dt, "n0", "n2")
        self.assertTrue(len(res_astar["road_path"]) > 0)
        self.assertTrue(len(res_astar["display_route"]) > 0)

        # 3. Dijkstra VRP Solver
        dijk_vrp = DijkstraVRPSolver().solve(self.problem)
        self.assertTrue(len(dijk_vrp.road_path) > 0)
        self.assertTrue(len(dijk_vrp.display_route) > 0)
        self.assertEqual(len(dijk_vrp.road_path), len(dijk_vrp.edge_path))

        # 4. QPSO VRP Solver
        qpso_vrp = QPSOVRPSolver(num_particles=10, max_iter=15, seed=42).solve(self.problem)
        self.assertTrue(len(qpso_vrp.road_path) > 0)
        self.assertTrue(len(qpso_vrp.display_route) > 0)
        self.assertEqual(len(qpso_vrp.road_path), len(qpso_vrp.edge_path))

        # 5. QAOA VRP Solver
        qaoa_vrp = QAOAVRPSolver().solve(self.problem, reps=1, shots=128)
        self.assertTrue(len(qaoa_vrp.road_path) > 0)
        self.assertTrue(len(qaoa_vrp.display_route) > 0)
        self.assertEqual(len(qaoa_vrp.road_path), len(qaoa_vrp.edge_path))

        # 6. ALNS VRP Solver
        alns_vrp = ALNSVRPSolver(max_iter=15, seed=42).solve(self.problem)
        self.assertTrue(len(alns_vrp.road_path) > 0)
        self.assertTrue(len(alns_vrp.display_route) > 0)
        self.assertEqual(len(alns_vrp.road_path), len(alns_vrp.edge_path))

        # 7. HGS VRP Solver
        hgs_vrp = HGSVRPSolver(pop_size=10, max_iter=15, seed=42).solve(self.problem)
        self.assertTrue(len(hgs_vrp.road_path) > 0)
        self.assertTrue(len(hgs_vrp.display_route) > 0)
        self.assertEqual(len(hgs_vrp.road_path), len(hgs_vrp.edge_path))

        # 8. Exact MIP VRP Solver
        mip_vrp = ExactMIPVRPSolver(time_limit_s=5.0).solve(self.problem)
        self.assertTrue(len(mip_vrp.road_path) > 0)
        self.assertTrue(len(mip_vrp.display_route) > 0)
        self.assertEqual(len(mip_vrp.road_path), len(mip_vrp.edge_path))

    def test_requirement_g_multi_vehicle_routes(self):
        """G. Multi-vehicle routes: Each FleetVehicleRoute has its own road_path and display_route."""
        res = DijkstraVRPSolver().solve(self.problem)
        self.assertEqual(len(res.fleet_routes), 2)

        for vr in res.fleet_routes:
            self.assertIsInstance(vr.road_path, list)
            self.assertIsInstance(vr.display_route, list)
            self.assertIsInstance(vr.route_steps, list)
            if vr.is_active:
                self.assertTrue(len(vr.road_path) > 0)
                self.assertEqual(len(vr.road_path), len(vr.edge_path))
                self.assertTrue(len(vr.display_route) > 0)
                # Check operational step guidance mentions road names
                self.assertTrue(any("Travel via" in step.get("action", "") for step in vr.operational_steps))

            # Verify dictionary serialization preserves these keys
            d = vr.to_dict()
            self.assertIn("road_path", d)
            self.assertIn("display_route", d)
            self.assertIn("route_steps", d)

    def test_requirement_h_dynamic_rerouting(self):
        """H. Dynamic rerouting: Before/after routes both contain road names in reroute_metadata."""
        rerouter = DynamicRerouter()
        initial_res = DijkstraVRPSolver().solve(self.problem)

        action, new_res, meta = rerouter.evaluate_rerouting_policy(
            self.problem,
            initial_res,
            active_incidents=["e01"],  # Incident blocking Shivaji Road
            solver_fn=lambda p: DijkstraVRPSolver().solve(p)
        )

        self.assertIn("old_roads", meta)
        self.assertIn("new_roads", meta)
        self.assertIsInstance(meta["old_roads"], list)
        self.assertIsInstance(meta["new_roads"], list)

    def test_requirement_i_incident_reporting_and_api(self):
        """I. Incident injection/clearing events and network API include street names."""
        road_name = self.dt.get_edge_road_name("e01")
        self.assertEqual(road_name, "Shivaji Road")

        unnamed = self.dt.get_edge_road_name("e25")
        self.assertEqual(unnamed, "Unnamed road")

        internal = self.dt.get_edge_road_name(":j1_0")
        self.assertEqual(internal, "Internal connector")

    def test_requirement_j_research_export(self):
        """J. Research export: JSON and CSV exports contain both edge_id and road_name fields."""
        res = DijkstraVRPSolver().solve(self.problem)
        res_dict = res.to_dict()

        # 1. JSON structure contains road_path, display_route, route_steps with road_name
        self.assertIn("road_path", res_dict)
        self.assertIn("display_route", res_dict)
        self.assertIn("route_steps", res_dict)
        for step in res_dict["route_steps"]:
            self.assertIn("edge_id", step)
            self.assertIn("road_name", step)

        # 2. Database save and CSV export
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            db_path = tf.name

        try:
            db = ExperimentDatabase(db_path=db_path)
            exp_id = "test_exp_road_names_01"
            db.save_experiment(
                experiment_id=exp_id,
                timestamp=100.0,
                graph_time=0.0,
                depot="n0",
                num_customers=2,
                num_vehicles=2,
                algorithm="dijkstra",
                seed=42,
                solution_dict=res_dict,
                total_cost=res.total_cost,
                total_travel_time=res.total_travel_time,
                total_distance=res.total_distance,
                runtime_ms=res.computation_time_ms,
                feasible=res.feasible,
            )

            csv_text = db.export_experiment_csv(exp_id)
            self.assertIn("display_route", csv_text)
            self.assertIn("road_path", csv_text)
            self.assertIn("edge_path", csv_text)
            self.assertIn("Shivaji Road", csv_text)
        finally:
            if os.path.exists(db_path):
                try:
                    os.remove(db_path)
                except Exception:
                    pass

    def test_real_sumo_network_road_names(self):
        """Integration test: Verify real OSM Pune network loads with authentic road names."""
        net_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "osm.net.xml.gz")
        if not os.path.exists(net_path):
            self.skipTest(f"SUMO network file {net_path} not found")

        real_graph = DynamicTrafficGraph()
        real_graph.load_net_file(net_path)

        # Check resolver is bound and has named edges
        self.assertIsNotNone(real_graph.road_resolver)
        named_edges = [meta["road_name"] for meta in real_graph.edge_metadata.values() if meta.get("road_name")]
        self.assertGreater(len(named_edges), 1000)

        # Check known Pune road names exist in the network
        unique_roads = set(named_edges)
        known_pune_roads = {"Shivaji Road", "Karve Road", "Jawaharlal Nehru Marg"}
        found_pune_roads = known_pune_roads.intersection(unique_roads)
        self.assertGreater(len(found_pune_roads), 0, f"Expected known Pune roads, found: {list(unique_roads)[:10]}")


if __name__ == '__main__':
    unittest.main()
