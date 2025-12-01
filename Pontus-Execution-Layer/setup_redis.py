#!/usr/bin/env python3
"""
Redis Setup Script
Tests and verifies Redis connection
"""
import asyncio
import sys

sys.path.insert(0, '/Users/arjundixit/Downloads/PontusExecution/Pontus-Execution-Layer')

from app.infra.redis_client import init_redis, cache_set, cache_get
from app.config import settings

print("=" * 80)
print("🔴 REDIS SETUP")
print("=" * 80)


async def setup_redis():
    """Set up and test Redis"""
    
    print("Step 1: Initializing Redis connection...")
    try:
        await init_redis()
        print("✅ Redis connection initialized\n")
    except Exception as e:
        print(f"❌ Redis initialization failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Redis is running:")
        print("   brew services start redis")
        print("   OR")
        print("   docker compose up -d redis")
        print("\n2. Check REDIS_URL in .env file")
        return False
    
    print("Step 2: Testing Redis operations...")
    try:
        # Test write
        await cache_set("test_key", {"test": "data"}, ttl=10)
        print("  ✅ Write operation successful")
        
        # Test read
        data = await cache_get("test_key")
        if data:
            print("  ✅ Read operation successful")
        else:
            print("  ❌ Read operation failed")
            return False
        
        # Cleanup
        # Note: We don't have a delete method, but TTL will handle it
        
        print("\n✅ Redis setup complete!")
        return True
        
    except Exception as e:
        print(f"❌ Redis test failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(setup_redis())
    sys.exit(0 if success else 1)

