"""
ArgMax Decision Layer
Normalizes and scores routes to select the optimal path using ArgMax.
"""
from typing import List, Dict, Tuple

from app.schemas.route_segment import RouteSegment

# Try to import numpy, fallback to manual argmin
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class ArgMaxDecisionLayer:
    """Decision layer for selecting optimal route using ArgMax"""
    
    def __init__(
        self,
        alpha: float = 0.4,  # Cost weight
        beta: float = 0.3,   # Speed weight
        gamma: float = 0.3   # Reliability weight
    ):
        """
        Initialize decision layer with weights.
        
        Args:
            alpha: Weight for cost (lower is better)
            beta: Weight for speed/latency (lower is better)
            gamma: Weight for reliability (higher is better)
        """
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
    
    def select_optimal_route(
        self,
        candidate_routes: List[Tuple[List[RouteSegment], Dict[str, float]]]
    ) -> Tuple[List[RouteSegment], Dict[str, float], float]:
        """
        Select optimal route from candidates using ArgMax.
        
        Args:
            candidate_routes: List of (path, metrics) tuples
            
        Returns:
            (optimal_path, metrics, score) tuple
        """
        if not candidate_routes:
            return None, {}, 0.0
        
        # Normalize metrics
        normalized_routes = []
        
        # Extract all metrics for normalization
        costs = [metrics['total_cost'] for _, metrics in candidate_routes]
        latencies = [metrics['total_latency'] for _, metrics in candidate_routes]
        reliabilities = [metrics['reliability'] for _, metrics in candidate_routes]
        
        # Calculate min/max for normalization
        min_cost = min(costs) if costs else 0.0
        max_cost = max(costs) if costs else 1.0
        cost_range = max_cost - min_cost if max_cost > min_cost else 1.0
        
        min_latency = min(latencies) if latencies else 0.0
        max_latency = max(latencies) if latencies else 1.0
        latency_range = max_latency - min_latency if max_latency > min_latency else 1.0
        
        min_reliability = min(reliabilities) if reliabilities else 0.0
        max_reliability = max(reliabilities) if reliabilities else 1.0
        reliability_range = max_reliability - min_reliability if max_reliability > min_reliability else 1.0
        
        # Normalize and score each route
        for path, metrics in candidate_routes:
            # Normalize cost (0 = best, 1 = worst)
            norm_cost = (metrics['total_cost'] - min_cost) / cost_range if cost_range > 0 else 0.0
            
            # Normalize latency (0 = best, 1 = worst)
            norm_latency = (metrics['total_latency'] - min_latency) / latency_range if latency_range > 0 else 0.0
            
            # Normalize reliability (0 = worst, 1 = best) - invert for consistency
            norm_reliability = 1.0 - ((metrics['reliability'] - min_reliability) / reliability_range if reliability_range > 0 else 0.0)
            
            # Calculate score (lower is better)
            score = (
                self.alpha * norm_cost +
                self.beta * norm_latency +
                self.gamma * norm_reliability
            )
            
            normalized_routes.append((path, metrics, score))
        
        # ArgMax: Find route with minimum score (best route)
        if HAS_NUMPY:
            optimal_idx = np.argmin([score for _, _, score in normalized_routes])
        else:
            # Manual argmin
            optimal_idx = min(range(len(normalized_routes)), key=lambda i: normalized_routes[i][2])
        optimal_path, optimal_metrics, optimal_score = normalized_routes[optimal_idx]
        
        return optimal_path, optimal_metrics, optimal_score
    
    def rank_routes(
        self,
        candidate_routes: List[Tuple[List[RouteSegment], Dict[str, float]]],
        top_k: int = 3
    ) -> List[Tuple[List[RouteSegment], Dict[str, float], float]]:
        """
        Rank routes and return top K.
        
        Returns:
            List of (path, metrics, score) tuples, sorted by score (best first)
        """
        if not candidate_routes:
            return []
        
        # Normalize and score (same as select_optimal_route)
        normalized_routes = []
        
        costs = [metrics['total_cost'] for _, metrics in candidate_routes]
        latencies = [metrics['total_latency'] for _, metrics in candidate_routes]
        reliabilities = [metrics['reliability'] for _, metrics in candidate_routes]
        
        min_cost = min(costs) if costs else 0.0
        max_cost = max(costs) if costs else 1.0
        cost_range = max_cost - min_cost if max_cost > min_cost else 1.0
        
        min_latency = min(latencies) if latencies else 0.0
        max_latency = max(latencies) if latencies else 1.0
        latency_range = max_latency - min_latency if max_latency > min_latency else 1.0
        
        min_reliability = min(reliabilities) if reliabilities else 0.0
        max_reliability = max(reliabilities) if reliabilities else 1.0
        reliability_range = max_reliability - min_reliability if max_reliability > min_reliability else 1.0
        
        for path, metrics in candidate_routes:
            norm_cost = (metrics['total_cost'] - min_cost) / cost_range if cost_range > 0 else 0.0
            norm_latency = (metrics['total_latency'] - min_latency) / latency_range if latency_range > 0 else 0.0
            norm_reliability = 1.0 - ((metrics['reliability'] - min_reliability) / reliability_range if reliability_range > 0 else 0.0)
            
            score = (
                self.alpha * norm_cost +
                self.beta * norm_latency +
                self.gamma * norm_reliability
            )
            
            normalized_routes.append((path, metrics, score))
        
        # Sort by score (lower is better)
        sorted_routes = sorted(normalized_routes, key=lambda x: x[2])
        
        return sorted_routes[:top_k]

