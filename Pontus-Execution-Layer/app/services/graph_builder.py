"""
Graph Builder Service
Converts route segments into a graph structure for optimization solvers.
"""
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
from app.schemas.route_segment import RouteSegment, SegmentType


class RouteGraph:
    """Represents a graph of route segments for pathfinding"""
    
    def __init__(self):
        # Graph structure: {node: {neighbor: [segments]}}
        self.graph: Dict[str, Dict[str, List[RouteSegment]]] = defaultdict(lambda: defaultdict(list))
        # All nodes (assets/networks)
        self.nodes: Set[str] = set()
        # Segment metadata
        self.segments: List[RouteSegment] = []
    
    def add_segment(self, segment: RouteSegment):
        """Add a route segment to the graph"""
        self.segments.append(segment)
        
        # Create node identifiers
        # For FX and bank_rail: just use asset
        # For crypto/bridge: use asset@network
        if segment.segment_type in [SegmentType.FX, SegmentType.BANK_RAIL]:
            from_node = segment.from_asset
            to_node = segment.to_asset
        else:
            from_node = f"{segment.from_asset}@{segment.from_network}" if segment.from_network else segment.from_asset
            to_node = f"{segment.to_asset}@{segment.to_network}" if segment.to_network else segment.to_asset
        
        self.nodes.add(from_node)
        self.nodes.add(to_node)
        self.graph[from_node][to_node].append(segment)
    
    def get_neighbors(self, node: str) -> Dict[str, List[RouteSegment]]:
        """Get all neighbors and segments for a node"""
        return self.graph.get(node, {})
    
    def get_segments(self, from_node: str, to_node: str) -> List[RouteSegment]:
        """Get all segments between two nodes"""
        return self.graph.get(from_node, {}).get(to_node, [])
    
    def find_paths(
        self,
        from_asset: str,
        to_asset: str,
        from_network: Optional[str] = None,
        to_network: Optional[str] = None,
        max_hops: int = 5
    ) -> List[List[RouteSegment]]:
        """
        Find all possible paths from source to destination using DFS.
        Returns list of paths, where each path is a list of segments.
        """
        # Normalize start/end nodes
        start_node = f"{from_asset}@{from_network}" if from_network else from_asset
        end_node = f"{to_asset}@{to_network}" if to_network else to_asset
        
        # Also try without network if network specified
        if from_network:
            start_nodes = [start_node, from_asset]
        else:
            start_nodes = [start_node]
        
        if to_network:
            end_nodes = [end_node, to_asset]
        else:
            end_nodes = [end_node]
        
        all_paths = []
        
        def dfs(current: str, path: List[RouteSegment], depth: int, visited: set):
            if depth > max_hops:
                return
            
            # Check if we reached destination (with or without network)
            if any(current == end or current.startswith(end + "@") for end in end_nodes):
                all_paths.append(path.copy())
                return
            
            if current in visited:
                return
            
            visited.add(current)
            
            # Try all neighbors
            neighbors = self.get_neighbors(current)
            for neighbor, segments_list in neighbors.items():
                for segment in segments_list:
                    # Determine next node based on segment type
                    if segment.segment_type in [SegmentType.FX, SegmentType.BANK_RAIL]:
                        next_node = segment.to_asset
                    else:
                        next_node = f"{segment.to_asset}@{segment.to_network}" if segment.to_network else segment.to_asset
                    
                    path.append(segment)
                    dfs(next_node, path, depth + 1, visited.copy())
                    path.pop()
            
            visited.remove(current)
        
        # Start DFS from all possible start nodes
        for start in start_nodes:
            if start in self.nodes:
                dfs(start, [], 0, set())
        
        return all_paths


class GraphBuilder:
    """Builds route graphs from route segments"""
    
    @staticmethod
    def build_graph(segments: List[RouteSegment]) -> RouteGraph:
        """Build a graph from route segments"""
        graph = RouteGraph()
        
        for segment in segments:
            graph.add_segment(segment)
        
        return graph
    
    @staticmethod
    def normalize_node(asset: str, network: Optional[str] = None, segment_type: SegmentType = None) -> str:
        """Normalize a node identifier"""
        if segment_type in [SegmentType.FX, SegmentType.BANK_RAIL]:
            return asset
        return f"{asset}@{network}" if network else asset

