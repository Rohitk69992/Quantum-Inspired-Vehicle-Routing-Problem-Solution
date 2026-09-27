from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from backend.graph.dynamic_graph import DynamicTrafficGraph

try:
    import traci
    TRACI_AVAILABLE = True
except ImportError:
    traci = None  # type: ignore
    TRACI_AVAILABLE = False


class EdgeMetadata(dict):
    """Dictionary subclass providing attribute-style and item-style access to edge metadata."""
    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'EdgeMetadata' object has no attribute '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value


class RoadMetadataResolver:
    """
    Central Authoritative Road Metadata and Street Name Resolution Engine.
    Directly extracts and resolves OpenStreetMap (OSM) road names from the loaded SUMO network.

    Key Invariants:
    1. SUMO edge IDs remain canonical machine identifiers.
    2. Road names are descriptive presentation metadata.
    3. Never hardcodes road names; extracts dynamically from network file / TraCI.
    4. Deterministic fallback: "Unnamed road" for missing names; "Internal connector" for internal edges (:junction...).
    5. Preserves 1-to-1 alignment: len(edge_path) == len(road_path).
    6. Compresses consecutive duplicate road names for human-readable display_route without altering edge_path.
    """

    def __init__(self, dt_graph: Optional[DynamicTrafficGraph] = None):
        self.dt_graph = dt_graph
        self._cache: Dict[str, EdgeMetadata] = {}

    def set_graph(self, dt_graph: DynamicTrafficGraph) -> None:
        """Binds a new DynamicTrafficGraph and clears stale cache."""
        self.dt_graph = dt_graph
        self._cache.clear()

    def load_from_dict(self, mapping: Dict[str, str]) -> None:
        """Populates edge_id -> road_name mappings directly (useful for tests or custom networks)."""
        for edge_id, name in mapping.items():
            rname = name.strip() if name and name.strip() else ("Internal connector" if edge_id.startswith(":") else "Unnamed road")
            self._cache[edge_id] = EdgeMetadata({
                "edge_id": edge_id,
                "road_name": rname,
                "from_node": "",
                "to_node": "",
                "length_m": 0.0,
                "speed_limit_ms": 13.89,
                "lane_count": 1,
                "travel_time_s": 0.0,
                "congestion_ratio": 0.0,
                "is_internal": edge_id.startswith(":"),
            })

    def resolve_edge(self, edge_id: str) -> EdgeMetadata:
        """
        Resolves a single SUMO edge ID to full authoritative metadata including road_name.
        Returns a structured dictionary with attribute access:
        {
            "edge_id": "123456#0",
            "road_name": "Baner Road",
            "from_node": "...",
            "to_node": "...",
            "length_m": 125.4,
            "speed_limit_ms": 13.89,
            "lane_count": 2,
            "travel_time_s": 9.03,
            "congestion_ratio": 0.0,
            "is_internal": False
        }
        """
        if not edge_id or not isinstance(edge_id, str):
            return EdgeMetadata({
                "edge_id": str(edge_id or ""),
                "road_name": "Unnamed road",
                "from_node": "",
                "to_node": "",
                "length_m": 0.0,
                "speed_limit_ms": 0.0,
                "lane_count": 1,
                "travel_time_s": 0.0,
                "congestion_ratio": 0.0,
                "is_internal": False,
            })

        # Check internal memory cache
        if edge_id in self._cache:
            return self._cache[edge_id]

        # Check if internal SUMO junction connector (starts with ':')
        if edge_id.startswith(":"):
            resolved = EdgeMetadata({
                "edge_id": edge_id,
                "road_name": "Internal connector",
                "from_node": "",
                "to_node": "",
                "length_m": 0.0,
                "speed_limit_ms": 13.89,
                "lane_count": 1,
                "travel_time_s": 0.0,
                "congestion_ratio": 0.0,
                "is_internal": True,
            })
            self._cache[edge_id] = resolved
            return resolved

        # Query DynamicTrafficGraph edge_metadata if available
        if self.dt_graph is not None and edge_id in self.dt_graph.edge_metadata:
            meta = self.dt_graph.edge_metadata[edge_id]
            road_name = meta.get("road_name")
            if not road_name or road_name.strip() == "":
                road_name = "Unnamed road"
            else:
                road_name = road_name.strip()

            resolved = EdgeMetadata({
                "edge_id": edge_id,
                "road_name": road_name,
                "from_node": meta.get("from_node", ""),
                "to_node": meta.get("to_node", ""),
                "length_m": round(float(meta.get("length", 0.0)), 2),
                "speed_limit_ms": round(float(meta.get("speed_limit", meta.get("mean_speed", 13.89))), 2),
                "lane_count": int(meta.get("lane_count", 1)),
                "travel_time_s": round(float(meta.get("travel_time", meta.get("free_flow_tt", 0.0))), 2),
                "congestion_ratio": round(float(meta.get("congestion_ratio", 0.0)), 3),
                "is_internal": False,
            })
            self._cache[edge_id] = resolved
            return resolved

        # Runtime TraCI fallback if simulation is running and edge not in static graph
        road_name = "Unnamed road"
        if TRACI_AVAILABLE and traci is not None:
            try:
                if traci.isLoaded():
                    street = traci.edge.getStreetName(edge_id)
                    if street and street.strip():
                        road_name = street.strip()
            except Exception:
                pass

        resolved = EdgeMetadata({
            "edge_id": edge_id,
            "road_name": road_name,
            "from_node": "",
            "to_node": "",
            "length_m": 0.0,
            "speed_limit_ms": 13.89,
            "lane_count": 1,
            "travel_time_s": 0.0,
            "congestion_ratio": 0.0,
            "is_internal": False,
        })
        self._cache[edge_id] = resolved
        return resolved

    def get_road_name(self, edge_id: str) -> str:
        """Returns only the human-readable road name for an edge ID."""
        return self.resolve_edge(edge_id)["road_name"]

    def compress_road_sequence(self, road_names: List[str], filter_internal: bool = True) -> List[str]:
        """
        Compresses consecutive duplicate road names for human-facing route presentation.
        Example:
            ['Baner Road', 'Baner Road', 'Pashan Road', 'Pashan Road']
            --> ['Baner Road', 'Pashan Road']

        If filter_internal is True, filters out intermediate 'Internal connector' entries,
        unless the entire sequence contains only internal connectors.
        """
        if not road_names:
            return []

        filtered = road_names
        if filter_internal:
            non_internal = [r for r in road_names if r != "Internal connector"]
            if non_internal:
                filtered = non_internal

        compressed: List[str] = []
        for name in filtered:
            clean_name = name.strip() if name else "Unnamed road"
            if not compressed or compressed[-1] != clean_name:
                compressed.append(clean_name)
        return compressed

    def resolve_edge_path(
        self, edge_path: Optional[List[str]]
    ) -> Tuple[List[str], List[str], List[Dict[str, Any]]]:
        """
        Resolves an edge path into:
        1. road_path: 1-to-1 corresponding road names (len(road_path) == len(edge_path)).
        2. display_route: compressed road names collapsing consecutive identical roads.
        3. route_steps: array of structured edge metadata dictionaries.
        """
        if not edge_path:
            return [], [], []

        route_steps: List[Dict[str, Any]] = []
        road_path: List[str] = []

        for eid in edge_path:
            meta = self.resolve_edge(eid)
            route_steps.append(meta)
            road_path.append(meta["road_name"])

        display_route = self.compress_road_sequence(road_path)
        return road_path, display_route, route_steps

    def format_human_route(
        self,
        visit_sequence: List[str],
        display_roads_by_leg: Optional[List[List[str]]] = None,
    ) -> str:
        """
        Formats a complete human-readable route string interweaving customer stops and road names.
        Example:
            'Depot (O) ➔ Baner Road ➔ Pashan Road ➔ Customer C1 ➔ University Road ➔ Depot (O)'
        """
        if not visit_sequence:
            return ""

        if not display_roads_by_leg:
            return " ➔ ".join(visit_sequence)

        parts: List[str] = []
        for idx in range(len(visit_sequence)):
            parts.append(visit_sequence[idx])
            if idx < len(display_roads_by_leg):
                leg_roads = display_roads_by_leg[idx]
                if leg_roads:
                    parts.extend(leg_roads)
        return " ➔ ".join(parts)


# Module-level singleton access
_GLOBAL_RESOLVER: Optional[RoadMetadataResolver] = None


def get_road_resolver(dt_graph: Optional[DynamicTrafficGraph] = None) -> RoadMetadataResolver:
    """Returns the central authoritative RoadMetadataResolver instance."""
    global _GLOBAL_RESOLVER
    if _GLOBAL_RESOLVER is None:
        _GLOBAL_RESOLVER = RoadMetadataResolver(dt_graph)
    elif dt_graph is not None and _GLOBAL_RESOLVER.dt_graph is not dt_graph:
        _GLOBAL_RESOLVER.set_graph(dt_graph)
    return _GLOBAL_RESOLVER


def set_road_resolver(resolver: RoadMetadataResolver) -> None:
    """Explicitly registers a RoadMetadataResolver instance."""
    global _GLOBAL_RESOLVER
    _GLOBAL_RESOLVER = resolver
