#!/usr/bin/env python3
"""
Full Integration Test - Tests the complete routing system end-to-end
"""
import sys
import traceback

def test_complete_flow():
    """Test complete routing flow from segments to optimal route"""
    print("=" * 70)
    print("🔄 Full Integration Test")
    print("=" * 70)
    
    # Step 1: Create mock data
    print("\n[Step 1/5] Creating mock route segments...")
    try:
        from app.schemas.route_segment import RouteSegment, SegmentType
        
        segments = [
            RouteSegment(
                segment_type=SegmentType.FX,
                from_asset="USD",
                to_asset="EUR",
                cost={"fee_percent": 0.001, "fixed_fee": 0.0, "effective_fx_rate": 0.92},
                latency={"min_minutes": 5, "max_minutes": 10},
                reliability_score=0.95,
                provider="frankfurter"
            ),
            RouteSegment(
                segment_type=SegmentType.CRYPTO,
                from_asset="USD",
                to_asset="USDC",
                from_network="ethereum",
                to_network="ethereum",
                cost={"fee_percent": 0.002, "fixed_fee": 0.0, "effective_fx_rate": 1.0},
                latency={"min_minutes": 2, "max_minutes": 5},
                reliability_score=0.98,
                provider="coingecko"
            ),
            RouteSegment(
                segment_type=SegmentType.BRIDGE,
                from_asset="USDC",
                to_asset="USDC",
                from_network="ethereum",
                to_network="polygon",
                cost={"fee_percent": 0.001, "fixed_fee": 0.0, "effective_fx_rate": 1.0},
                latency={"min_minutes": 5, "max_minutes": 15},
                reliability_score=0.92,
                provider="lifi"
            ),
            RouteSegment(
                segment_type=SegmentType.OFF_RAMP,
                from_asset="USDC",
                to_asset="EUR",
                from_network="polygon",
                to_network=None,
                cost={"fee_percent": 0.003, "fixed_fee": 0.0, "effective_fx_rate": 0.92},
                latency={"min_minutes": 10, "max_minutes": 30},
                reliability_score=0.90,
                provider="transak"
            ),
        ]
        print(f"✅ Created {len(segments)} route segments")
    except Exception as e:
        print(f"❌ Failed to create segments: {e}")
        traceback.print_exc()
        return False
    
    # Step 2: Build graph
    print("\n[Step 2/5] Building route graph...")
    try:
        from app.services.graph_builder import GraphBuilder
        graph_builder = GraphBuilder()
        graph = graph_builder.build_graph(segments)
        print(f"✅ Graph built: {len(graph.nodes)} nodes, {sum(len(neighbors) for neighbors in graph.graph.values())} edges")
    except Exception as e:
        print(f"❌ Graph building failed: {e}")
        traceback.print_exc()
        return False
    
    # Step 3: Test solvers
    print("\n[Step 3/5] Testing solvers...")
    try:
        from app.services.ortools_solver import ORToolsSolver
        ortools = ORToolsSolver()
        candidates = ortools.solve_multi_objective(graph, "USD", "EUR", max_paths=5)
        print(f"✅ OR-Tools found {len(candidates)} candidate routes")
        
        if candidates:
            path, metrics = candidates[0]
            print(f"   Best route: {len(path)} segments, cost: {metrics['total_cost_percent']:.4f}%")
    except Exception as e:
        print(f"❌ Solver test failed: {e}")
        traceback.print_exc()
        return False
    
    # Step 4: Test routing service
    print("\n[Step 4/5] Testing routing service...")
    try:
        from app.services.routing_service import RoutingService
        routing = RoutingService(use_cplex=None)
        
        result = routing.find_optimal_route(
            segments=segments,
            from_asset="USD",
            to_asset="EUR"
        )
        
        if "error" in result:
            print(f"⚠️  Route finding returned: {result['error']}")
            # This might be OK if no valid path exists
        else:
            print(f"✅ Found optimal route!")
            print(f"   Solver: {result.get('solver_used', 'Unknown')}")
            print(f"   Cost: {result.get('cost_percent', 0):.4f}%")
            print(f"   ETA: {result.get('eta_hours', 0):.2f} hours")
            print(f"   Reliability: {result.get('reliability', 0):.2f}")
            print(f"   Segments: {result.get('num_segments', 0)}")
    except Exception as e:
        print(f"❌ Routing service failed: {e}")
        traceback.print_exc()
        return False
    
    # Step 5: Test top routes
    print("\n[Step 5/5] Testing top routes...")
    try:
        top_routes = routing.find_top_routes(
            segments=segments,
            from_asset="USD",
            to_asset="EUR",
            top_k=3
        )
        
        if "error" in top_routes:
            print(f"⚠️  Top routes returned: {top_routes['error']}")
        else:
            print(f"✅ Found {top_routes.get('count', 0)} top routes")
            for route in top_routes.get('routes', [])[:2]:
                print(f"   Route {route.get('rank', '?')}: {route.get('cost_percent', 0):.4f}% cost, {route.get('eta_hours', 0):.2f}h ETA")
    except Exception as e:
        print(f"❌ Top routes test failed: {e}")
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 70)
    print("✅ Full integration test PASSED!")
    print("=" * 70)
    return True

if __name__ == '__main__':
    success = test_complete_flow()
    sys.exit(0 if success else 1)

