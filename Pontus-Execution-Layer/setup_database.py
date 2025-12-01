#!/usr/bin/env python3
"""
Database Setup Script
Initializes PostgreSQL database and populates initial route data
"""
import asyncio
import sys
from datetime import datetime

import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Update database URL to use current user if not set
if not os.getenv("DATABASE_URL"):
    import getpass
    username = getpass.getuser()
    os.environ["DATABASE_URL"] = f"postgresql+asyncpg://{username}@localhost:5432/routing_db"

from app.infra.database import init_db, AsyncSessionLocal
from app.services.aggregator_service import AggregatorService
from app.config import settings

print("=" * 80)
print("🗄️  DATABASE SETUP")
print("=" * 80)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


async def setup_database():
    """Set up database and populate initial data"""
    
    print("Step 1: Initializing database schema...")
    try:
        await init_db()
        print("✅ Database schema initialized\n")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure PostgreSQL is running:")
        print("   brew services start postgresql@15")
        print("   OR")
        print("   docker compose up -d postgres")
        print("\n2. Create database if needed:")
        print("   createdb routing_db")
        print("\n3. Check DATABASE_URL in .env file")
        return False
    
    print("Step 2: Testing database connection...")
    try:
        async with AsyncSessionLocal() as session:
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            result.scalar()
            print("✅ Database connection successful\n")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    print("Step 3: Populating initial route data...")
    try:
        aggregator = AggregatorService()
        
        # Fetch segments from all sources
        print("  Fetching FX rates...")
        fx_segments = await aggregator.clients["fx"].fetch_segments()
        print(f"    ✅ Found {len(fx_segments)} FX segments")
        
        print("  Fetching crypto prices...")
        crypto_segments = await aggregator.clients["crypto"].fetch_segments()
        print(f"    ✅ Found {len(crypto_segments)} crypto segments")
        
        print("  Fetching gas fees...")
        gas_segments = await aggregator.clients["gas"].fetch_segments()
        print(f"    ✅ Found {len(gas_segments)} gas segments")
        
        print("  Fetching bridge quotes...")
        bridge_segments = await aggregator.clients["bridge"].fetch_segments()
        print(f"    ✅ Found {len(bridge_segments)} bridge segments")
        
        print("  Fetching bank rail data...")
        bank_segments = await aggregator.clients["bank_rail"].fetch_segments()
        print(f"    ✅ Found {len(bank_segments)} bank rail segments")
        
        print("  Fetching liquidity data...")
        liquidity_segments = await aggregator.clients["liquidity"].fetch_segments()
        print(f"    ✅ Found {len(liquidity_segments)} liquidity segments")
        
        # Combine all segments
        all_segments = fx_segments + crypto_segments + gas_segments + bridge_segments + bank_segments + liquidity_segments
        
        print(f"\n  Total segments fetched: {len(all_segments)}")
        
        # Cache segments
        print("  Caching segments in Redis...")
        await aggregator.cache_segments(all_segments)
        print("    ✅ Segments cached")
        
        # Persist to database
        print("  Persisting segments to database...")
        await aggregator.persist_segments(all_segments)
        print(f"    ✅ {len(all_segments)} segments persisted")
        
        # Create snapshot
        print("  Creating snapshot...")
        await aggregator.persist_snapshot(all_segments)
        print("    ✅ Snapshot created")
        
        await aggregator.close()
        
        print("\n✅ Database setup complete!")
        print(f"   Total route segments: {len(all_segments)}")
        return True
        
    except Exception as e:
        print(f"❌ Error populating data: {e}")
        import traceback
        traceback.print_exc()
        return False


async def verify_setup():
    """Verify database setup"""
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    
    try:
        aggregator = AggregatorService()
        
        # Check cached segments
        cached = await aggregator.get_cached_segments()
        print(f"✅ Cached segments: {len(cached)}")
        
        # Check database segments
        db_segments = await aggregator.get_segments_from_db(limit=1000)
        print(f"✅ Database segments: {len(db_segments)}")
        
        # Check snapshot
        snapshot = await aggregator.get_latest_snapshot()
        if snapshot:
            print(f"✅ Latest snapshot: {snapshot.get('count', 0)} segments")
        
        await aggregator.close()
        
        if len(db_segments) > 0:
            print("\n✅ Database setup verified successfully!")
            return True
        else:
            print("\n⚠️  Database is set up but no segments found")
            return False
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False


async def main():
    """Main setup function"""
    success = await setup_database()
    
    if success:
        verify_success = await verify_setup()
        
        if verify_success:
            print("\n" + "=" * 80)
            print("🎉 SETUP COMPLETE!")
            print("=" * 80)
            print("\nDatabase is ready. You can now:")
            print("  1. Start the server: python -m app.main")
            print("  2. Test routes: curl http://localhost:8000/api/routes/optimize?from_asset=USD&to_asset=EUR")
            print("  3. Execute routes: POST /api/routes/execute")
            return True
    
    print("\n" + "=" * 80)
    print("⚠️  SETUP INCOMPLETE")
    print("=" * 80)
    print("\nPlease check the errors above and try again.")
    return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

