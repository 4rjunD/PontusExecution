"""
OR-Tools Routing Solver
Uses Google OR-Tools for shortest path and multi-objective optimization.
"""
from typing import List, Dict, Optional, Tuple
import math
import logging

logger = logging.getLogger(__name__)

# Try to import OR-Tools graph module (may not be available in all versions)
try:
    from ortools.graph import pywrapgraph
    ORTOOLS_AVAILABLE = True
except ImportError:
    try:
        # Try alternative import path
        from ortools.graph.python import min_cost_flow
        ORTOOLS_AVAILABLE = True
        pywrapgraph = None  # Will use alternative
    except ImportError:
        ORTOOLS_AVAILABLE = False
        pywrapgraph = None
        logger.warning("OR-Tools graph module not available. Using fallback graph search.")

from app.schemas.route_segment import RouteSegment
from app.services.graph_builder import RouteGraph


class ORToolsSolver:
    """OR-Tools based routing solver"""
    
    def __init__(
        self,
        cost_weight: float = 1.0,
        latency_weight: float = 1.0,
        reliability_weight: float = 1.0
    ):
        """
        Initialize solver with weights for multi-objective optimization.
        
        Args:
            cost_weight: Weight for cost minimization
            latency_weight: Weight for latency minimization
            reliability_weight: Weight for reliability maximization
        """
        self.cost_weight = cost_weight
        self.latency_weight = latency_weight
        self.reliability_weight = reliability_weight
    
    def solve_shortest_path(
        self,
        graph: RouteGraph,
        from_asset: str,
        to_asset: str,
        from_network: Optional[str] = None,
        to_network: Optional[str] = None
    ) -> Optional[List[RouteSegment]]:
        """
        Solve shortest path using OR-Tools.
        Uses combined cost, latency, and reliability as edge weights.
        """
        # Build node mapping
        nodes = list(graph.nodes)
        node_to_index = {node: i for i, node in enumerate(nodes)}
        index_to_node = {i: node for node, i in node_to_index.items()}
        
        # Check if OR-Tools is available
        if not ORTOOLS_AVAILABLE or pywrapgraph is None:
            # Fall back to graph search
            logger.warning("OR-Tools not available, using graph search fallback")
            return self._fallback_graph_search(graph, from_asset, to_asset, from_network, to_network)
        
        # Create graph for OR-Tools
        # OR-Tools uses SimpleMinCostFlow for shortest path
        min_cost_flow = pywrapgraph.SimpleMinCostFlow()
        
        # Add edges
        edge_to_segment = {}  # Map (from_idx, to_idx) -> best segment
        
        for from_node, neighbors in graph.graph.items():
            from_idx = node_to_index[from_node]
            
            for to_node, segments_list in neighbors.items():
                to_idx = node_to_index[to_node]
                
                # Find best segment (lowest combined cost)
                best_segment = None
                best_cost = float('inf')
                
                for segment in segments_list:
                    # Calculate combined cost
                    cost = self._calculate_edge_cost(segment)
                    
                    if cost < best_cost:
                        best_cost = cost
                        best_segment = segment
                
                if best_segment:
                    # Add edge to OR-Tools graph
                    # Capacity = 1, Cost = combined cost
                    min_cost_flow.AddArcWithCapacityAndUnitCost(
                        from_idx, to_idx, 1, int(best_cost * 1000000)  # Scale for integer
                    )
                    edge_to_segment[(from_idx, to_idx)] = best_segment
        
        # Set source and sink
        start_node = f"{from_asset}@{from_network}" if from_network else from_asset
        end_node = f"{to_asset}@{to_network}" if to_network else to_asset
        
        # Try to find start/end indices
        start_idx = None
        end_idx = None
        
        for node, idx in node_to_index.items():
            if node == start_node or (from_network and node == from_asset):
                start_idx = idx
            if node == end_node or (to_network and node == to_asset):
                end_idx = idx
        
        if start_idx is None or end_idx is None:
            return None
        
        # Set supplies
        min_cost_flow.SetNodeSupply(start_idx, 1)
        min_cost_flow.SetNodeSupply(end_idx, -1)
        
        # Solve
        status = min_cost_flow.Solve()
        
        if status != min_cost_flow.OPTIMAL:
            return None
        
        # Reconstruct path
        path_segments = []
        current = start_idx
        
        while current != end_idx:
            # Find next node in path
            found = False
            for arc in range(min_cost_flow.NumArcs()):
                if min_cost_flow.Tail(arc) == current and min_cost_flow.Flow(arc) > 0:
                    next_idx = min_cost_flow.Head(arc)
                    segment = edge_to_segment.get((current, next_idx))
                    if segment:
                        path_segments.append(segment)
                        current = next_idx
                        found = True
                        break
            
            if not found:
                return None
        
        return path_segments if path_segments else None
    
    def solve_multi_objective(
        self,
        graph: RouteGraph,
        from_asset: str,
        to_asset: str,
        from_network: Optional[str] = None,
        to_network: Optional[str] = None,
        max_paths: int = 10
    ) -> List[Tuple[List[RouteSegment], Dict[str, float]]]:
        """
        Find multiple candidate paths with different tradeoffs.
        Returns list of (path, metrics) tuples.
        """
        # Use DFS to find all paths, then rank by different objectives
        all_paths = graph.find_paths(from_asset, to_asset, from_network, to_network)
        
        if not all_paths:
            return []
        
        # Calculate metrics for each path
        path_metrics = []
        for path in all_paths:
            metrics = self._calculate_path_metrics(path)
            path_metrics.append((path, metrics))
        
        # Sort by different objectives and return top paths
        # 1. Cost-optimized
        cost_sorted = sorted(path_metrics, key=lambda x: x[1]['total_cost'])
        # 2. Latency-optimized
        latency_sorted = sorted(path_metrics, key=lambda x: x[1]['total_latency'])
        # 3. Reliability-optimized
        reliability_sorted = sorted(path_metrics, key=lambda x: -x[1]['reliability'])
        # 4. Combined score
        combined_sorted = sorted(path_metrics, key=lambda x: x[1]['combined_score'])
        
        # Collect unique top paths
        seen_paths = set()
        result = []
        
        for path_list in [cost_sorted, latency_sorted, reliability_sorted, combined_sorted]:
            for path, metrics in path_list[:max_paths]:
                path_id = tuple(seg.id for seg in path if seg.id)
                if path_id not in seen_paths:
                    seen_paths.add(path_id)
                    result.append((path, metrics))
                    if len(result) >= max_paths:
                        break
            if len(result) >= max_paths:
                break
        
        return result
    
    def _fallback_graph_search(
        self,
        graph: RouteGraph,
        from_asset: str,
        to_asset: str,
        from_network: Optional[str] = None,
        to_network: Optional[str] = None
    ) -> Optional[List[RouteSegment]]:
        """Fallback to graph search when OR-Tools is not available"""
        paths = graph.find_paths(from_asset, to_asset, from_network, to_network, max_hops=5)
        if not paths:
            return None
        
        # Return the path with lowest cost
        best_path = None
        best_cost = float('inf')
        
        for path in paths:
            metrics = self._calculate_path_metrics(path)
            cost = metrics['combined_score']
            if cost < best_cost:
                best_cost = cost
                best_path = path
        
        return best_path
    
    def _calculate_edge_cost(self, segment: RouteSegment) -> float:
        """Calculate combined edge cost for optimization"""
        # Extract cost components
        fee_percent = segment.cost.get('fee_percent', 0.0)
        fixed_fee = segment.cost.get('fixed_fee', 0.0)
        
        # Normalize latency (convert minutes to cost-equivalent)
        min_latency = segment.latency.get('min_minutes', 0)
        max_latency = segment.latency.get('max_minutes', 0)
        avg_latency = (min_latency + max_latency) / 2 if max_latency > 0 else min_latency
        latency_cost = avg_latency / 60.0  # Convert minutes to hours, then normalize
        
        # Reliability (invert so lower is better)
        reliability_penalty = (1.0 - segment.reliability_score) * 0.1
        
        # Combined cost
        combined = (
            self.cost_weight * (fee_percent + fixed_fee * 0.0001) +
            self.latency_weight * latency_cost +
            self.reliability_weight * reliability_penalty
        )
        
        return combined
    
    def _calculate_path_metrics(self, path: List[RouteSegment]) -> Dict[str, float]:
        """Calculate total metrics for a path"""
        total_cost_percent = 0.0
        total_fixed_fee = 0.0
        total_min_latency = 0
        total_max_latency = 0
        reliability_scores = []
        
        for segment in path:
            total_cost_percent += segment.cost.get('fee_percent', 0.0)
            total_fixed_fee += segment.cost.get('fixed_fee', 0.0)
            total_min_latency += segment.latency.get('min_minutes', 0)
            total_max_latency += segment.latency.get('max_minutes', 0)
            reliability_scores.append(segment.reliability_score)
        
        # Average reliability
        avg_reliability = sum(reliability_scores) / len(reliability_scores) if reliability_scores else 0.0
        
        # Combined score (lower is better)
        avg_latency_hours = ((total_min_latency + total_max_latency) / 2) / 60.0
        combined_score = (
            self.cost_weight * (total_cost_percent + total_fixed_fee * 0.0001) +
            self.latency_weight * avg_latency_hours +
            self.reliability_weight * (1.0 - avg_reliability)
        )
        
        return {
            'total_cost': total_cost_percent + total_fixed_fee * 0.0001,
            'total_cost_percent': total_cost_percent,
            'total_fixed_fee': total_fixed_fee,
            'total_latency': (total_min_latency + total_max_latency) / 2,
            'min_latency': total_min_latency,
            'max_latency': total_max_latency,
            'reliability': avg_reliability,
            'combined_score': combined_score,
            'num_segments': len(path)
        }

