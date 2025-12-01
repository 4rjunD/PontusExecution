# Setup Guide

## Quick Start (Minimal Setup)

The application will work **without any API keys** for basic functionality. Many services have free tiers or work without authentication.

### 1. Start Services

```bash
docker-compose up -d
```

This starts PostgreSQL and Redis.

### 2. Run the Application

```bash
pip install -r requirements.txt
python -m app.main
```

The app will start and begin fetching data from available sources.

## API Keys (Optional but Recommended)

While the app works without keys, some services will have rate limits or limited functionality. Here's what you can optionally configure:

### Free/No Key Required (Works Out of the Box)

✅ **Frankfurter API** - No key needed, free FX rates  
✅ **ECB (European Central Bank)** - Public API  
✅ **Binance** - Public price API (no key needed for basic quotes)  
✅ **Hard-coded Bank Rail Fees** - Always available  
✅ **Regulatory Constraints** - Loaded from local JSON file  

### Optional API Keys (Improves Rate Limits & Features)

#### Low Priority (Nice to Have)
- **ExchangeRate API** (`EXCHANGERATE_API_KEY`)
  - Free tier: 1,500 requests/month
  - Get free key at: https://www.exchangerate-api.com/
  - Without key: Uses demo mode (limited)

- **CoinGecko** (`COINGECKO_API_KEY`)
  - Free tier: 10-50 calls/minute
  - Get free key at: https://www.coingecko.com/en/api
  - Without key: Uses public API (rate limited)

#### Medium Priority (Better Data Quality)
- **Etherscan** (`ETHERSCAN_API_KEY`)
  - Free tier: 5 calls/second
  - Get free key at: https://etherscan.io/apis
  - Without key: Uses default token (very limited)

- **Polygonscan** (`POLYGONSCAN_API_KEY`)
  - Free tier: 5 calls/second
  - Get free key at: https://polygonscan.com/apis
  - Without key: Uses default token (very limited)

#### High Priority (For Production)
- **Socket** (`SOCKET_API_KEY`)
  - Required for bridge quotes
  - Get key at: https://docs.socket.tech/
  - Without key: May not work

- **LI.FI** (`LIFI_API_KEY`)
  - Required for bridge quotes
  - Get key at: https://li.fi/
  - Without key: May not work

- **0x** (`ZEROX_API_KEY`)
  - Improves liquidity data
  - Get key at: https://0x.org/docs/api
  - Without key: May have rate limits

#### On/Off-Ramp (For Testing)
- **Transak** (`TRANSAK_API_KEY`)
  - For on/off-ramp quotes
  - Get key at: https://transak.com/
  - Without key: May not work

- **Onmeta** (`ONMETA_API_KEY`)
  - For on/off-ramp quotes (test mode)
  - Get key at: https://onmeta.in/
  - Without key: May not work

## Configuration

### Option 1: Environment Variables

Create a `.env` file in the project root:

```bash
# Database (defaults work with docker-compose)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/routing_db
REDIS_URL=redis://localhost:6379/0

# Optional API Keys
EXCHANGERATE_API_KEY=your_key_here
ETHERSCAN_API_KEY=your_key_here
POLYGONSCAN_API_KEY=your_key_here
COINGECKO_API_KEY=your_key_here
SOCKET_API_KEY=your_key_here
LIFI_API_KEY=your_key_here
TRANSAK_API_KEY=your_key_here
ONMETA_API_KEY=your_key_here
ZEROX_API_KEY=your_key_here
```

### Option 2: Edit config.py

You can also hardcode keys in `app/config.py` (not recommended for production).

## What Works Without Keys?

Even without any API keys, you'll still get:

1. ✅ **FX Rates** - From Frankfurter and ECB (free, no key)
2. ✅ **Crypto Prices** - From Binance public API
3. ✅ **Bank Rail Estimates** - From hard-coded fee table
4. ✅ **Regulatory Constraints** - From local JSON file
5. ⚠️ **Gas Fees** - Limited (Etherscan/Polygonscan need keys for reliable access)
6. ⚠️ **Bridges** - May not work (Socket/LI.FI need keys)
7. ⚠️ **On/Off-Ramp** - May not work (Transak/Onmeta need keys)
8. ⚠️ **Liquidity** - May have rate limits (0x needs key for production)

## Testing the Setup

1. Start the app: `python -m app.main`
2. Check health: `curl http://localhost:8000/health`
3. View API docs: Open http://localhost:8000/docs in your browser
4. Test endpoints:
   - `GET /api/routes/segments` - Should return segments
   - `GET /api/quotes/fx?from_currency=USD&to_currency=EUR` - Should return FX quotes

## Troubleshooting

### Services won't start
```bash
# Check if Docker is running
docker ps

# Check logs
docker-compose logs
```

### No data in responses
- Check that background tasks are running (check console output)
- Wait a few seconds for initial data fetch
- Check Redis: `docker exec -it potenuse-redis-1 redis-cli KEYS "*"`
- Check database: Connect to Postgres and query `route_segments` table

### Rate limit errors
- Add API keys to increase rate limits
- Some services have generous free tiers

## Next Steps

1. **For Development**: Start with no keys, add them as needed
2. **For Production**: Get keys for Socket, LI.FI, and 0x at minimum
3. **For Testing**: The app will work with mock/fallback data in many cases

The application is designed to gracefully handle missing API keys and will continue working with available data sources.

