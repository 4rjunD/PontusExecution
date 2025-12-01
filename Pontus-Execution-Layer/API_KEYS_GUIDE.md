# API Keys Guide - What You Need vs What's Already Working

## ✅ ALREADY WORKING (No Keys Needed - Start Here!)

These work **right now** without any setup:

### FX Rates (100% Working)
- ✅ **Frankfurter API** - Free, no key, unlimited
- ✅ **ECB (European Central Bank)** - Free, no key, public API
- ✅ **ExchangeRate API** - Uses "demo" key (limited but works)

### Crypto Prices (100% Working)
- ✅ **Binance** - Public API, no key needed
- ✅ **CoinGecko** - Works without key (10-50 calls/min free tier)

### Liquidity (100% Working)
- ✅ **Uniswap Subgraph** - Public GraphQL API, no key needed

### Bank Rails (100% Working)
- ✅ **Hard-coded Fee Table** - Always available, no API needed

### Regulatory (100% Working)
- ✅ **Local JSON File** - Loaded from `data/regulatory_constraints.json`

---

## ⚠️ NEEDS KEYS (But Has Fallbacks - Low Priority)

These work with defaults but are **very limited**:

### Gas Fees (Works but Limited)
- ⚠️ **Etherscan** - Uses default token "YourApiKeyToken" (5 calls/sec limit)
  - **Get free key**: https://etherscan.io/apis
  - **Why**: Better rate limits (5 calls/sec → unlimited with key)
  
- ⚠️ **Polygonscan** - Uses default token "YourApiKeyToken" (5 calls/sec limit)
  - **Get free key**: https://polygonscan.com/apis
  - **Why**: Better rate limits

**Priority**: LOW - Works with defaults, just limited

---

## 🔴 NEEDS KEYS (May Not Work - High Priority for Production)

These **may fail** without keys:

### Bridges (Critical for Cross-Chain)
- 🔴 **Socket** - Checks for key, may return errors without
  - **Get key**: https://docs.socket.tech/
  - **Why**: Required for bridge quotes
  - **Priority**: HIGH for production

- 🔴 **LI.FI** - Checks for key, may return errors without
  - **Get key**: https://li.fi/ (contact for API access)
  - **Why**: Required for bridge quotes
  - **Priority**: HIGH for production

### On/Off-Ramp (For Fiat ↔ Crypto)
- 🔴 **Transak** - Checks for key, may return errors without
  - **Get key**: https://transak.com/ (developer portal)
  - **Why**: Required for on/off-ramp quotes
  - **Priority**: MEDIUM (only if you need fiat ramps)

- 🔴 **Onmeta** - Checks for key, may return errors without
  - **Get key**: https://onmeta.in/ (developer portal)
  - **Why**: Required for on/off-ramp quotes
  - **Priority**: MEDIUM (only if you need fiat ramps)

### Liquidity (Better Data)
- 🟡 **0x** - Works without key but rate limited
  - **Get key**: https://0x.org/docs/api
  - **Why**: Better rate limits for production
  - **Priority**: MEDIUM (works without, but better with)

---

## 📋 ACTION PLAN

### For Immediate Testing (Right Now)
**Do nothing!** Just run:
```bash
docker-compose up -d
python -m app.main
```

You'll get:
- ✅ FX rates (Frankfurter, ECB)
- ✅ Crypto prices (Binance, CoinGecko)
- ✅ Liquidity data (Uniswap)
- ✅ Bank rail estimates (hard-coded)
- ⚠️ Gas fees (limited with defaults)
- ❌ Bridges (may fail)
- ❌ On/off-ramp (may fail)

### For Development (Get These First)
1. **Etherscan API Key** (2 minutes)
   - Go to: https://etherscan.io/apis
   - Sign up (free)
   - Copy API key
   - Add to `.env`: `ETHERSCAN_API_KEY=your_key`

2. **Polygonscan API Key** (2 minutes)
   - Go to: https://polygonscan.com/apis
   - Sign up (free)
   - Copy API key
   - Add to `.env`: `POLYGONSCAN_API_KEY=your_key`

### For Production (Get These)
1. **Socket API Key** (Required for bridges)
   - Go to: https://docs.socket.tech/
   - Sign up for API access
   - Add to `.env`: `SOCKET_API_KEY=your_key`

2. **LI.FI API Key** (Required for bridges)
   - Go to: https://li.fi/
   - Contact for API access
   - Add to `.env`: `LIFI_API_KEY=your_key`

3. **0x API Key** (Better liquidity data)
   - Go to: https://0x.org/docs/api
   - Sign up (free tier available)
   - Add to `.env`: `ZEROX_API_KEY=your_key`

### Optional (Only if you need fiat ramps)
- **Transak API Key**: https://transak.com/
- **Onmeta API Key**: https://onmeta.in/

---

## 🎯 Quick Setup (Copy-Paste Ready)

Create `.env` file:

```bash
# Database (defaults work)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/routing_db
REDIS_URL=redis://localhost:6379/0

# Get these first (free, 2 min each)
ETHERSCAN_API_KEY=
POLYGONSCAN_API_KEY=

# Get these for production (bridges)
SOCKET_API_KEY=
LIFI_API_KEY=

# Optional (better rate limits)
ZEROX_API_KEY=
COINGECKO_API_KEY=
EXCHANGERATE_API_KEY=

# Only if you need fiat ramps
TRANSAK_API_KEY=
ONMETA_API_KEY=
```

---

## Summary

**What's Already Done:**
- ✅ FX rates (3 providers, all working)
- ✅ Crypto prices (2 providers, all working)
- ✅ Liquidity (Uniswap, working)
- ✅ Bank rails (hard-coded, always works)
- ✅ Regulatory (local file, always works)

**What You Should Get:**
1. **Etherscan** + **Polygonscan** (free, 2 min each) - For gas fees
2. **Socket** + **LI.FI** (if you need bridges) - For cross-chain routing
3. **0x** (optional) - For better liquidity data

**Total Time to Get Essential Keys: ~5 minutes** (just Etherscan + Polygonscan)

Everything else is optional and depends on your use case!

