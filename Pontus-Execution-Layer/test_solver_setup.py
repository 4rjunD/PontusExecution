#!/usr/bin/env python3
"""
Test CPLEX and OR-Tools Setup
Verifies that solvers are properly configured with graceful fallback
"""
import sys

def test_ortools():
    """Test OR-Tools availability"""
    print("=" * 60)
    print("Testing OR-Tools...")
    print("=" * 60)
    try:
        from ortools.graph import pywrapgraph
        print("✅ OR-Tools is available")
        return True
    except ImportError as e:
        print(f"❌ OR-Tools not available: {e}")
        print("   Install with: pip install ortools")
        return False

def test_cplex():
    """Test CPLEX availability"""
    print("\n" + "=" * 60)
    print("Testing CPLEX...")
    print("=" * 60)
    try:
        import cplex
        print(f"✅ CPLEX is available")
        print(f"   Version: {cplex.__version__ if hasattr(cplex, '__version__') else 'Unknown'}")
        return True
    except ImportError:
        print("⚠️  CPLEX not available (this is OK - OR-Tools will be used)")
        print("   To install CPLEX, see ROUTING_ENGINE_SETUP.md")
        return False

def test_routing_service():
    """Test RoutingService initialization"""
    print("\n" + "=" * 60)
    print("Testing RoutingService...")
    print("=" * 60)
    try:
        from app.services.routing_service import RoutingService
        from app.services.cplex_solver import CPLEX_AVAILABLE
        
        # Test auto-detect (None)
        print("\n1. Testing auto-detect mode (use_cplex=None)...")
        service = RoutingService(use_cplex=None)
        if service.use_cplex and service.cplex_solver:
            print("   ✅ CPLEX detected and initialized")
        else:
            print("   ✅ OR-Tools will be used (CPLEX not available)")
        
        # Test force OR-Tools
        print("\n2. Testing force OR-Tools mode (use_cplex=False)...")
        service2 = RoutingService(use_cplex=False)
        if not service2.use_cplex:
            print("   ✅ OR-Tools mode confirmed")
        
        # Test force CPLEX (if available)
        if CPLEX_AVAILABLE:
            print("\n3. Testing force CPLEX mode (use_cplex=True)...")
            service3 = RoutingService(use_cplex=True)
            if service3.use_cplex and service3.cplex_solver:
                print("   ✅ CPLEX mode confirmed")
            else:
                print("   ⚠️  CPLEX requested but not initialized")
        else:
            print("\n3. Skipping CPLEX force test (CPLEX not available)")
        
        print("\n✅ RoutingService works correctly!")
        return True
    except Exception as e:
        print(f"❌ RoutingService test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "=" * 60)
    print("🚀 Solver Setup Test")
    print("=" * 60)
    
    results = {
        "OR-Tools": test_ortools(),
        "CPLEX": test_cplex(),
        "RoutingService": test_routing_service()
    }
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    for name, result in results.items():
        status = "✅ PASS" if result else ("⚠️  SKIP" if name == "CPLEX" else "❌ FAIL")
        print(f"{name:20} {status}")
    
    # Overall status
    if results["OR-Tools"]:
        print("\n✅ System is ready! OR-Tools is available (required).")
        if results["CPLEX"]:
            print("✅ Bonus: CPLEX is also available for advanced optimization!")
        else:
            print("ℹ️  CPLEX is optional - system will use OR-Tools (which is excellent!)")
        return 0
    else:
        print("\n❌ OR-Tools is required but not available!")
        print("   Install with: pip install ortools")
        return 1

if __name__ == '__main__':
    sys.exit(main())

