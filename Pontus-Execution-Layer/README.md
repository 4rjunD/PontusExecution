# Route Intelligence Layer - Cross-Border Routing Optimizer

A FastAPI-based data layer for aggregating and normalizing routing data from multiple sources including FX rates, crypto prices, gas fees, bridges, on/off-ramps, bank rails, and liquidity providers.

## Features

- **Data Adapters**: Multiple clients for fetching data from various providers
- **Normalization Layer**: Unified RouteSegment model for all data types
- **Caching**: Redis caching with configurable TTL
- **Persistence**: PostgreSQL storage with SQLAlchemy
- **Background Tasks**: Automated data refresh at different intervals
- **REST API**: FastAPI endpoints for querying route data

## Tech Stack

- FastAPI
- httpx (async HTTP client)
- Redis (caching)
- PostgreSQL (SQLAlchemy)
- Pydantic (data validation)
- Alembic (optional migrations)

## Project Structure

```
app/
  main.py                 # Application entry point
  config.py              # Configuration settings
  api/
    routes_data.py       # API endpoints
  clients/               # Data adapter clients
    fx_client.py
    crypto_client.py
    gas_client.py
    bridge_client.py
    ramp_client.py
    bank_rail_client.py
    liquidity_client.py
    regulatory_client.py
  services/
    aggregator_service.py # Aggregation and normalization
  schemas/
    route_segment.py     # Pydantic schemas
    quotes.py
  models/
    route_segment.py     # SQLAlchemy models
  infra/
    database.py          # Database setup
    redis_client.py      # Redis client
  tasks/
    background_tasks.py  # Background refresh tasks
data/
  regulatory_constraints.json
```

## Setup

### Quick Start (No API Keys Required!)

The application works **out of the box** without any API keys. Many services have free public APIs.

1. **Start services with Docker Compose**:
```bash
docker-compose up -d
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the application**:
```bash
python -m app.main
```

Or with uvicorn:
```bash
uvicorn app.main:app --reload
```

4. **Test it**: Open http://localhost:8000/docs to see the API documentation

### Optional: Add API Keys (For Better Rate Limits)

See [SETUP.md](SETUP.md) for detailed information about optional API keys. The app will work without them, but adding keys improves:
- Rate limits
- Data quality
- Access to premium features (bridges, on/off-ramps)

**Minimum setup**: Just run `docker-compose up -d` and `python -m app.main` - that's it!

## API Endpoints

### Health Check
- `GET /health` - Health check endpoint

### Route Segments
- `GET /api/routes/segments` - Get route segments with optional filters
  - Query params: `segment_type`, `from_asset`, `to_asset`, `use_cache`, `limit`

### Quotes
- `GET /api/quotes/fx` - Get FX quotes
  - Query params: `from_currency`, `to_currency`
- `GET /api/quotes/crypto` - Get crypto quotes
  - Query params: `from_asset`, `to_asset`, `from_network`, `to_network`
- `GET /api/quotes/gas` - Get gas quotes
  - Query params: `network`

### Snapshots
- `GET /api/snapshots/latest` - Get latest snapshot of all segments

## Background Tasks

- **Fast refresh (2s)**: Crypto prices, gas fees, bridge quotes
- **Slow refresh (30-60s)**: FX rates, bank rails, liquidity data
- **Full refresh (60s)**: Complete snapshot of all segments

## Data Sources

### FX
- Frankfurter API
- ExchangeRate API
- ECB (European Central Bank)

### Crypto
- CoinGecko
- Binance

### Gas Fees
- Etherscan
- Polygonscan

### Bridges
- Socket
- LI.FI

### On/Off-Ramp
- Transak
- Onmeta

### Bank Rails
- Wise
- Remitly
- Hard-coded fee table

### Liquidity
- 0x
- Uniswap Subgraph

### Regulatory
- Local JSON file with constraints

## Configuration

Edit `app/config.py` or set environment variables to configure:
- Database connection
- Redis connection
- API keys for various services
- Refresh intervals

## Development

The application uses async/await throughout for optimal performance. All HTTP calls are made asynchronously, and data is cached in Redis before being persisted to PostgreSQL.

