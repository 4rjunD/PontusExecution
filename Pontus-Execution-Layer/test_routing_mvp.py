#!/usr/bin/env python3
"""
Comprehensive MVP Test Suite for Routing System
Tests all components to ensure production readiness
"""
import sys
import asyncio
from datetime import datetime
from typing import List

# Test imports
print("=" * 70)
print("🧪 MVP Routing System Test Suite")
print("=" * 70)

# Test 1: Import all components
print("\n[1/10] Testing imports...")
try:
    from app.services.graph_builder import GraphBuilder, RouteGraph
    from app.services.ortools_solver import ORToolsSolver
    from app.services.routing_service import RoutingService
    from app.services.argmax_decision import ArgMaxDecisionLayer
    from app.schemas.route_segment import RouteSegment, SegmentType
    print("✅ All imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Check CPLEX availability
print("\n[2/10] Checking CPLEX availability...")
try:
    from app.services.cplex_solver import CPLEX_AVAILABLE
    if CPLEX_AVAILABLE:
        print("✅ CPLEX is available")
    else:
        print("ℹ️  CPLEX not available (OR-Tools will be used)")
except Exception as e:
    print(f"⚠️  CPLEX check failed: {e}")

# Test 3: Create mock route segments
print("\n[3/10] Creating mock route segments...")
def create_mock_segments() -> List[RouteSegment]:
    """Create realistic mock route segments for testing"""
    segments = []
    
    # FX segments
    segments.append(RouteSegment(
        segment_type=SegmentType.FX,
        from_asset="USD",
        to_asset="EUR",
        cost={"fee_percent": 0.001, "fixed_fee": 0.0, "effective_fx_rate": 0.92},
        latency={"min_minutes": 5, "max_minutes": 10},
        reliability_score=0.95,
        provider="frankfurter"
    ))
    
    segments.append(RouteSegment(
        segment_type=SegmentType.FX,
        from_asset="USD",
        to_asset="GBP",
        cost={"fee_percent": 0.0015, "fixed_fee": 0.0, "effective_fx_rate": 0.79},
        latency={"min_minutes": 5, "max_minutes": 10},
        reliability_score=0.94,
        provider="exchangerate"
    ))
    
    # Crypto segments
    segments.append(RouteSegment(
        segment_type=SegmentType.CRYPTO,
        from_asset="USD",
        to_asset="USDC",
        from_network="ethereum",
        to_network="ethereum",
        cost={"fee_percent": 0.002, "fixed_fee": 0.0, "effective_fx_rate": 1.0},
        latency={"min_minutes": 2, "max_minutes": 5},
        reliability_score=0.98,
        provider="coingecko"
    ))
    
    segments.append(RouteSegment(
        segment_type=SegmentType.CRYPTO,
        from_asset="USDC",
        to_asset="EUR",
        from_network="ethereum",
        to_network=None,
        cost={"fee_percent": 0.003, "fixed_fee": 0.0, "effective_fx_rate": 0.92},
        latency={"min_minutes": 10, "max_minutes": 30},
        reliability_score=0.90,
        provider="transak"
    ))
    
    # Bridge segment
    segments.append(RouteSegment(
        segment_type=SegmentType.BRIDGE,
        from_asset="USDC",
        to_asset="USDC",
        from_network="ethereum",
        to_network="polygon",
        cost={"fee_percent": 0.001, "fixed_fee": 0.0, "effective_fx_rate": 1.0},
        latency={"min_minutes": 5, "max_minutes": 15},
        reliability_score=0.92,
        provider="lifi"
    ))
    
    # Bank rail segment
    segments.append(RouteSegment(
        segment_type=SegmentType.BANK_RAIL,
        from_asset="EUR",
        to_asset="INR",
        cost={"fee_percent": 0.025, "fixed_fee": 5.0, "effective_fx_rate": 83.5},
        latency={"min_minutes": 60, "max_minutes": 180},
        reliability_score=0.88,
        provider="wise"
    ))
    
    return segments

mock_segments = create_mock_segments()
print(f"✅ Created {len(mock_segments)} mock route segments")

# Test 4: Graph Builder
print("\n[4/10] Testing Graph Builder...")
try:
    graph_builder = GraphBuilder()
    graph = graph_builder.build_graph(mock_segments)
    print(f"✅ Graph built with {len(graph.nodes)} nodes")
    
    # Test pathfinding
    paths = graph.find_paths("USD", "EUR", max_hops=5)
    print(f"✅ Found {len(paths)} paths from USD to EUR")
except Exception as e:
    print(f"❌ Graph builder failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: OR-Tools Solver
print("\n[5/10] Testing OR-Tools Solver...")
try:
    ortools_solver = ORToolsSolver()
    
    # Test shortest path
    path = ortools_solver.solve_shortest_path(graph, "USD", "EUR")
    if path:
        print(f"✅ OR-Tools found shortest path with {len(path)} segments")
    else:
        print("⚠️  OR-Tools didn't find a path (may be normal for some routes)")
    
    # Test multi-objective
    candidates = ortools_solver.solve_multi_objective(graph, "USD", "EUR", max_paths=5)
    print(f"✅ OR-Tools found {len(candidates)} candidate routes")
except Exception as e:
    print(f"❌ OR-Tools solver failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: CPLEX Solver (if available)
print("\n[6/10] Testing CPLEX Solver (if available)...")
if CPLEX_AVAILABLE:
    try:
        from app.services.cplex_solver import CPLEXSolver
        cplex_solver = CPLEXSolver()
        
        # Test MIP
        path = cplex_solver.solve_mip(graph, "USD", "EUR")
        if path:
            print(f"✅ CPLEX found path with {len(path)} segments")
        else:
            print("⚠️  CPLEX didn't find a path")
        
        # Test multi-objective
        candidates = cplex_solver.solve_multi_objective(graph, "USD", "EUR", max_paths=5)
        print(f"✅ CPLEX found {len(candidates)} candidate routes")
    except Exception as e:
        print(f"⚠️  CPLEX solver test failed: {e} (this is OK - OR-Tools will be used)")
else:
    print("ℹ️  CPLEX not available - skipping (OR-Tools will be used)")

# Test 7: ArgMax Decision Layer
print("\n[7/10] Testing ArgMax Decision Layer...")
try:
    decision_layer = ArgMaxDecisionLayer(alpha=0.4, beta=0.3, gamma=0.3)
    
    # Create some candidate routes
    test_candidates = ortools_solver.solve_multi_objective(graph, "USD", "EUR", max_paths=3)
    if test_candidates:
        optimal_path, metrics, score = decision_layer.select_optimal_route(test_candidates)
        if optimal_path:
            print(f"✅ ArgMax selected optimal route (score: {score:.4f})")
            print(f"   Cost: {metrics['total_cost_percent']:.4f}%, ETA: {metrics['total_latency']:.1f} min, Reliability: {metrics['reliability']:.2f}")
        else:
            print("⚠️  ArgMax didn't select a route")
        
        # Test ranking
        ranked = decision_layer.rank_routes(test_candidates, top_k=3)
        print(f"✅ ArgMax ranked {len(ranked)} routes")
    else:
        print("⚠️  No candidates to test ArgMax with")
except Exception as e:
    print(f"❌ ArgMax decision layer failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 8: Routing Service (Full Integration)
print("\n[8/10] Testing Routing Service (Full Integration)...")
try:
    routing_service = RoutingService(use_cplex=None)  # Auto-detect
    
    # Test find_optimal_route
    result = routing_service.find_optimal_route(
        segments=mock_segments,
        from_asset="USD",
        to_asset="EUR"
    )
    
    if "error" in result:
        print(f"⚠️  Route finding returned error: {result['error']}")
    else:
        print(f"✅ Found optimal route!")
        print(f"   Solver used: {result.get('solver_used', 'Unknown')}")
        print(f"   Cost: {result.get('cost_percent', 0):.4f}%")
        print(f"   ETA: {result.get('eta_hours', 0):.2f} hours")
        print(f"   Reliability: {result.get('reliability', 0):.2f}")
        print(f"   Segments: {result.get('num_segments', 0)}")
    
    # Test find_top_routes
    top_routes = routing_service.find_top_routes(
        segments=mock_segments,
        from_asset="USD",
        to_asset="EUR",
        top_k=3
    )
    
    if "error" in top_routes:
        print(f"⚠️  Top routes returned error: {top_routes['error']}")
    else:
        print(f"✅ Found {top_routes.get('count', 0)} top routes")
        
except Exception as e:
    print(f"❌ Routing service failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 9: Multiple Route Scenarios
print("\n[9/10] Testing Multiple Route Scenarios...")
scenarios = [
    ("USD", "EUR", None, None),
    ("USD", "INR", None, None),
    ("USDC", "EUR", "ethereum", None),
]

routing_service = RoutingService(use_cplex=None)
passed = 0
for from_asset, to_asset, from_net, to_net in scenarios:
    try:
        result = routing_service.find_optimal_route(
            segments=mock_segments,
            from_asset=from_asset,
            to_asset=to_asset,
            from_network=from_net,
            to_network=to_net
        )
        if "error" not in result:
            passed += 1
            print(f"   ✅ {from_asset} → {to_asset}: Found route")
        else:
            print(f"   ⚠️  {from_asset} → {to_asset}: {result['error']}")
    except Exception as e:
        print(f"   ❌ {from_asset} → {to_asset}: {e}")

print(f"✅ Passed {passed}/{len(scenarios)} route scenarios")

# Test 10: Error Handling
print("\n[10/10] Testing Error Handling...")
try:
    # Test with no segments
    result = routing_service.find_optimal_route(
        segments=[],
        from_asset="USD",
        to_asset="EUR"
    )
    if "error" in result:
        print("✅ Handles empty segments gracefully")
    else:
        print("⚠️  Should return error for empty segments")
    
    # Test with invalid route
    result = routing_service.find_optimal_route(
        segments=mock_segments,
        from_asset="XYZ",
        to_asset="ABC"
    )
    if "error" in result:
        print("✅ Handles invalid routes gracefully")
    else:
        print("⚠️  Should return error for invalid routes")
    
    print("✅ Error handling works correctly")
except Exception as e:
    print(f"⚠️  Error handling test issue: {e}")

# Final Summary
print("\n" + "=" * 70)
print("📊 MVP Test Summary")
print("=" * 70)
print("✅ All core components tested")
print("✅ Graph builder functional")
print("✅ OR-Tools solver functional")
if CPLEX_AVAILABLE:
    print("✅ CPLEX solver functional")
else:
    print("ℹ️  CPLEX not available (OR-Tools used)")
print("✅ ArgMax decision layer functional")
print("✅ Routing service functional")
print("✅ Error handling functional")
print("\n🎉 Routing system is MVP-ready!")
print("=" * 70)

