"""
CPLEX Routing Solver
Uses IBM CPLEX for mixed-integer programming and advanced optimization.
Note: CPLEX requires separate installation. Falls back gracefully if not available.
"""
from typing import List, Dict, Optional, Tuple
import logging

from app.schemas.route_segment import RouteSegment
from app.services.graph_builder import RouteGraph

logger = logging.getLogger(__name__)

# Try to import CPLEX
try:
    import cplex
    CPLEX_AVAILABLE = True
except ImportError:
    CPLEX_AVAILABLE = False
    logger.warning("CPLEX not available. Install IBM CPLEX Community Edition for advanced optimization.")


class CPLEXSolver:
    """CPLEX-based routing solver for advanced optimization"""
    
    def __init__(
        self,
        cost_weight: float = 1.0,
        latency_weight: float = 1.0,
        reliability_weight: float = 1.0
    ):
        """
        Initialize CPLEX solver with weights for multi-objective optimization.
        
        Args:
            cost_weight: Weight for cost minimization
            latency_weight: Weight for latency minimization
            reliability_weight: Weight for reliability maximization
        """
        if not CPLEX_AVAILABLE:
            raise ImportError(
                "CPLEX is not installed. "
                "Please install IBM CPLEX Community Edition. "
                "See installation instructions in README."
            )
        
        self.cost_weight = cost_weight
        self.latency_weight = latency_weight
        self.reliability_weight = reliability_weight
    
    def solve_mip(
        self,
        graph: RouteGraph,
        from_asset: str,
        to_asset: str,
        from_network: Optional[str] = None,
        to_network: Optional[str] = None
    ) -> Optional[List[RouteSegment]]:
        """
        Solve routing problem using Mixed-Integer Programming.
        Uses binary variables to select edges in the path.
        """
        # Build node mapping
        nodes = list(graph.nodes)
        node_to_index = {node: i for i, node in enumerate(nodes)}
        
        # Identify start and end nodes
        start_node = f"{from_asset}@{from_network}" if from_network else from_asset
        end_node = f"{to_asset}@{to_network}" if to_network else to_asset
        
        start_idx = node_to_index.get(start_node) or node_to_index.get(from_asset)
        end_idx = node_to_index.get(end_node) or node_to_index.get(to_asset)
        
        if start_idx is None or end_idx is None:
            return None
        
        # Build edge list with costs
        edges = []
        edge_to_segment = {}
        edge_index = 0
        
        for from_node, neighbors in graph.graph.items():
            from_idx = node_to_index[from_node]
            
            for to_node, segments_list in neighbors.items():
                to_idx = node_to_index[to_node]
                
                # Find best segment
                best_segment = None
                best_cost = float('inf')
                
                for segment in segments_list:
                    cost = self._calculate_edge_cost(segment)
                    if cost < best_cost:
                        best_cost = cost
                        best_segment = segment
                
                if best_segment:
                    edges.append((from_idx, to_idx, best_cost))
                    edge_to_segment[edge_index] = best_segment
                    edge_index += 1
        
        if not edges:
            return None
        
        # Create CPLEX model
        model = cplex.Cplex()
        model.set_results_stream(None)  # Suppress output
        
        # Variables: binary for each edge (1 if used, 0 otherwise)
        var_names = [f"edge_{i}" for i in range(len(edges))]
        obj_coeffs = [cost for _, _, cost in edges]
        
        model.variables.add(
            obj=obj_coeffs,
            types=[model.variables.type.binary] * len(edges),
            names=var_names
        )
        
        # Constraints: Flow conservation
        # For each node: sum(incoming) - sum(outgoing) = supply
        for node_idx in range(len(nodes)):
            incoming = []
            outgoing = []
            
            for i, (from_idx, to_idx, _) in enumerate(edges):
                if to_idx == node_idx:
                    incoming.append(var_names[i])
                if from_idx == node_idx:
                    outgoing.append(var_names[i])
            
            # Supply: +1 for start, -1 for end, 0 for others
            if node_idx == start_idx:
                supply = 1
            elif node_idx == end_idx:
                supply = -1
            else:
                supply = 0
            
            # Constraint: sum(incoming) - sum(outgoing) = supply
            if incoming or outgoing:
                constraint = []
                coeffs = []
                
                for var in incoming:
                    constraint.append([(var_names.index(var), 1.0)])
                    coeffs.append(1.0)
                
                for var in outgoing:
                    constraint.append([(var_names.index(var), -1.0)])
                    coeffs.append(-1.0)
                
                if constraint:
                    model.linear_constraints.add(
                        lin_expr=constraint,
                        senses=['E'],
                        rhs=[supply]
                    )
        
        # Solve
        try:
            model.solve()
            
            if model.solution.get_status() != model.solution.status.optimal:
                return None
            
            # Extract solution
            solution = model.solution.get_values()
            path_segments = []
            
            # Reconstruct path
            current = start_idx
            visited_edges = set()
            
            while current != end_idx:
                found = False
                for i, (from_idx, to_idx, _) in enumerate(edges):
                    if from_idx == current and solution[i] > 0.5 and i not in visited_edges:
                        segment = edge_to_segment[i]
                        path_segments.append(segment)
                        current = to_idx
                        visited_edges.add(i)
                        found = True
                        break
                
                if not found:
                    return None
            
            return path_segments if path_segments else None
            
        except Exception as e:
            logger.error(f"CPLEX solve error: {e}")
            return None
        finally:
            model.end()
    
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
        Find multiple candidate paths using different objective weights.
        """
        # Find all candidate paths first
        all_paths = graph.find_paths(from_asset, to_asset, from_network, to_network)
        
        if not all_paths:
            return []
        
        # Calculate metrics for each path
        path_metrics = []
        for path in all_paths:
            metrics = self._calculate_path_metrics(path)
            path_metrics.append((path, metrics))
        
        # Use CPLEX to solve weighted combinations
        # For now, return top paths sorted by different objectives
        cost_sorted = sorted(path_metrics, key=lambda x: x[1]['total_cost'])
        latency_sorted = sorted(path_metrics, key=lambda x: x[1]['total_latency'])
        reliability_sorted = sorted(path_metrics, key=lambda x: -x[1]['reliability'])
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
    
    def _calculate_edge_cost(self, segment: RouteSegment) -> float:
        """Calculate combined edge cost"""
        fee_percent = segment.cost.get('fee_percent', 0.0)
        fixed_fee = segment.cost.get('fixed_fee', 0.0)
        
        min_latency = segment.latency.get('min_minutes', 0)
        max_latency = segment.latency.get('max_minutes', 0)
        avg_latency = (min_latency + max_latency) / 2 if max_latency > 0 else min_latency
        latency_cost = avg_latency / 60.0
        
        reliability_penalty = (1.0 - segment.reliability_score) * 0.1
        
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
        
        avg_reliability = sum(reliability_scores) / len(reliability_scores) if reliability_scores else 0.0
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

