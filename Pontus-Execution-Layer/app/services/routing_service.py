"""
Routing Service
Orchestrates graph building, solvers, and decision layer to find optimal routes.
"""
from typing import List, Dict, Optional, Tuple
import logging

from app.schemas.route_segment import RouteSegment
from app.services.graph_builder import GraphBuilder, RouteGraph
from app.services.ortools_solver import ORToolsSolver
from app.services.argmax_decision import ArgMaxDecisionLayer

logger = logging.getLogger(__name__)

# Try to import CPLEX solver
try:
    from app.services.cplex_solver import CPLEXSolver, CPLEX_AVAILABLE
except ImportError:
    CPLEX_AVAILABLE = False
    logger.info("CPLEX solver not available")


class RoutingService:
    """Main routing service that coordinates all components"""
    
    def __init__(
        self,
        use_cplex: bool = None,  # None = auto-detect, True = force CPLEX, False = force OR-Tools
        cost_weight: float = 1.0,
        latency_weight: float = 1.0,
        reliability_weight: float = 1.0,
        alpha: float = 0.4,
        beta: float = 0.3,
        gamma: float = 0.3
    ):
        """
        Initialize routing service.
        
        Args:
            use_cplex: Whether to use CPLEX solver (None = auto-detect, True = force CPLEX, False = force OR-Tools)
            cost_weight: Weight for cost in optimization
            latency_weight: Weight for latency in optimization
            reliability_weight: Weight for reliability in optimization
            alpha: Cost weight in ArgMax decision
            beta: Speed weight in ArgMax decision
            gamma: Reliability weight in ArgMax decision
        """
        self.graph_builder = GraphBuilder()
        self.ortools_solver = ORToolsSolver(
            cost_weight=cost_weight,
            latency_weight=latency_weight,
            reliability_weight=reliability_weight
        )
        
        # Auto-detect CPLEX if use_cplex is None, otherwise use specified preference
        if use_cplex is None:
            # Auto-detect: use CPLEX if available, otherwise use OR-Tools
            self.use_cplex = CPLEX_AVAILABLE
            if self.use_cplex:
                logger.info("CPLEX detected and will be used as primary solver (OR-Tools as fallback)")
            else:
                logger.info("CPLEX not available, using OR-Tools as primary solver")
        else:
            self.use_cplex = use_cplex and CPLEX_AVAILABLE
        
        # Initialize CPLEX solver if requested and available
        self.cplex_solver = None
        if self.use_cplex:
            try:
                self.cplex_solver = CPLEXSolver(
                    cost_weight=cost_weight,
                    latency_weight=latency_weight,
                    reliability_weight=reliability_weight
                )
                logger.info("CPLEX solver initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize CPLEX solver: {e}. Falling back to OR-Tools.")
                self.use_cplex = False
                self.cplex_solver = None
        else:
            # Ensure cplex_solver is None if not using CPLEX
            self.cplex_solver = None
        
        self.decision_layer = ArgMaxDecisionLayer(
            alpha=alpha,
            beta=beta,
            gamma=gamma
        )
    
    def find_optimal_route(
        self,
        segments: List[RouteSegment],
        from_asset: str,
        to_asset: str,
        from_network: Optional[str] = None,
        to_network: Optional[str] = None,
        max_candidates: int = 20
    ) -> Dict:
        """
        Find optimal route from source to destination.
        
        Returns:
            Dictionary with:
            - route: List of segments
            - cost_percent: Total cost as percentage
            - eta_hours: Estimated time in hours
            - reliability: Reliability score (0-1)
            - segments: Detailed segment information
            - solver_used: Which solver was used
        """
        # Build graph
        graph = self.graph_builder.build_graph(segments)
        
        # Find candidate routes using solvers
        # Try CPLEX first if available, then OR-Tools as fallback
        candidate_routes = []
        solver_used = "Graph Search"
        
        # Try CPLEX first (if available and enabled)
        if self.use_cplex and self.cplex_solver:
            try:
                cplex_candidates = self.cplex_solver.solve_multi_objective(
                    graph=graph,
                    from_asset=from_asset,
                    to_asset=to_asset,
                    from_network=from_network,
                    to_network=to_network,
                    max_paths=max_candidates
                )
                if cplex_candidates:
                    candidate_routes.extend(cplex_candidates)
                    solver_used = "CPLEX"
                    logger.debug(f"CPLEX found {len(cplex_candidates)} candidate routes")
            except Exception as e:
                logger.warning(f"CPLEX solver error: {e}. Falling back to OR-Tools.")
                # Continue to OR-Tools fallback
        
        # Use OR-Tools (always available as fallback or primary)
        try:
            ortools_candidates = self.ortools_solver.solve_multi_objective(
                graph=graph,
                from_asset=from_asset,
                to_asset=to_asset,
                from_network=from_network,
                to_network=to_network,
                max_paths=max_candidates
            )
            if ortools_candidates:
                candidate_routes.extend(ortools_candidates)
                if solver_used == "CPLEX":
                    solver_used = "CPLEX + OR-Tools"
                elif solver_used == "Graph Search":
                    solver_used = "OR-Tools"
                logger.debug(f"OR-Tools found {len(ortools_candidates)} candidate routes")
        except Exception as e:
            logger.error(f"OR-Tools solver error: {e}")
            # Will fall back to graph search if both solvers fail
        
        # If no candidates from solvers, use graph search
        if not candidate_routes:
            all_paths = graph.find_paths(from_asset, to_asset, from_network, to_network)
            if all_paths:
                # Calculate metrics for graph search paths
                for path in all_paths[:max_candidates]:
                    metrics = self.ortools_solver._calculate_path_metrics(path)
                    candidate_routes.append((path, metrics))
                solver_used = "Graph Search"
        
        if not candidate_routes:
            return {
                "error": "No route found",
                "from_asset": from_asset,
                "to_asset": to_asset
            }
        
        # Use ArgMax to select optimal route
        optimal_path, optimal_metrics, optimal_score = self.decision_layer.select_optimal_route(
            candidate_routes
        )
        
        if not optimal_path:
            return {
                "error": "Failed to select optimal route",
                "candidates": len(candidate_routes)
            }
        
        # Format response
        return {
            "route": [
                {
                    "segment_type": seg.segment_type.value,
                    "from_asset": seg.from_asset,
                    "to_asset": seg.to_asset,
                    "from_network": seg.from_network,
                    "to_network": seg.to_network,
                    "provider": seg.provider,
                    "cost": seg.cost,
                    "latency": seg.latency,
                    "reliability_score": seg.reliability_score
                }
                for seg in optimal_path
            ],
            "cost_percent": round(optimal_metrics['total_cost_percent'], 4),
            "cost_fixed": round(optimal_metrics['total_fixed_fee'], 2),
            "eta_hours": round(optimal_metrics['total_latency'] / 60.0, 2),
            "eta_minutes": round(optimal_metrics['total_latency'], 0),
            "reliability": round(optimal_metrics['reliability'], 2),
            "num_segments": optimal_metrics['num_segments'],
            "solver_used": solver_used,
            "score": round(optimal_score, 4)
        }
    
    def find_top_routes(
        self,
        segments: List[RouteSegment],
        from_asset: str,
        to_asset: str,
        from_network: Optional[str] = None,
        to_network: Optional[str] = None,
        top_k: int = 3,
        max_candidates: int = 20
    ) -> Dict:
        """
        Find top K routes ranked by optimality.
        
        Returns:
            Dictionary with list of top routes
        """
        # Build graph
        graph = self.graph_builder.build_graph(segments)
        
        # Find candidate routes
        # Try CPLEX first if available, then OR-Tools as fallback
        candidate_routes = []
        
        # Try CPLEX first (if available and enabled)
        if self.use_cplex and self.cplex_solver:
            try:
                cplex_candidates = self.cplex_solver.solve_multi_objective(
                    graph=graph,
                    from_asset=from_asset,
                    to_asset=to_asset,
                    from_network=from_network,
                    to_network=to_network,
                    max_paths=max_candidates
                )
                if cplex_candidates:
                    candidate_routes.extend(cplex_candidates)
            except Exception as e:
                logger.warning(f"CPLEX solver error: {e}. Falling back to OR-Tools.")
        
        # Use OR-Tools (always available as fallback or primary)
        try:
            ortools_candidates = self.ortools_solver.solve_multi_objective(
                graph=graph,
                from_asset=from_asset,
                to_asset=to_asset,
                from_network=from_network,
                to_network=to_network,
                max_paths=max_candidates
            )
            if ortools_candidates:
                candidate_routes.extend(ortools_candidates)
        except Exception as e:
            logger.error(f"OR-Tools solver error: {e}")
        
        if not candidate_routes:
            all_paths = graph.find_paths(from_asset, to_asset, from_network, to_network)
            if all_paths:
                for path in all_paths[:max_candidates]:
                    metrics = self.ortools_solver._calculate_path_metrics(path)
                    candidate_routes.append((path, metrics))
        
        if not candidate_routes:
            return {
                "error": "No routes found",
                "from_asset": from_asset,
                "to_asset": to_asset
            }
        
        # Rank routes
        ranked_routes = self.decision_layer.rank_routes(candidate_routes, top_k=top_k)
        
        # Format response
        routes = []
        for rank, (path, metrics, score) in enumerate(ranked_routes, 1):
            routes.append({
                "rank": rank,
                "route": [
                    {
                        "segment_type": seg.segment_type.value,
                        "from_asset": seg.from_asset,
                        "to_asset": seg.to_asset,
                        "from_network": seg.from_network,
                        "to_network": seg.to_network,
                        "provider": seg.provider,
                        "cost": seg.cost,
                        "latency": seg.latency,
                        "reliability_score": seg.reliability_score
                    }
                    for seg in path
                ],
                "cost_percent": round(metrics['total_cost_percent'], 4),
                "cost_fixed": round(metrics['total_fixed_fee'], 2),
                "eta_hours": round(metrics['total_latency'] / 60.0, 2),
                "eta_minutes": round(metrics['total_latency'], 0),
                "reliability": round(metrics['reliability'], 2),
                "num_segments": metrics['num_segments'],
                "score": round(score, 4)
            })
        
        return {
            "routes": routes,
            "count": len(routes)
        }

