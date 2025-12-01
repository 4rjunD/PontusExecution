# B. Routing Engine (Core Optimizer) - ARJUN

**Purpose:**
Generate the cheapest, fastest, and most reliable route using formal optimization.

**Data Sources Available (from Part A):**
- **FX Rates:** Frankfurter API, ExchangeRate API (USD ↔ EUR, GBP, JPY, CAD, etc.)
- **Gas Prices:** Etherscan API (Ethereum), Polygon RPC (Polygon)
- **Crypto Prices:** CoinGecko API (BTC, ETH, USDC, USDT)
- **Bridge Quotes:** LI.FI API (Ethereum ↔ Polygon cross-chain)
- **Bank Rails:** Hard-coded fee table (USD ↔ EUR, GBP, CAD, MXN)
- **On/Off-Ramps:** Transak, Onmeta (available but may require API keys)

**Components included:**

## 1. OR-Tools Optimization (free)
Use Google OR-Tools to compute:
- Shortest path
- Multi weight path
- Constraint based routing
- Multi objective optimization

## 2. CPLEX Optimization (free community edition)
Use CPLEX Community Edition for:
- Mixed integer programming
- Multi objective cost and latency tradeoff
- Reliability weighted constraints
- Strict route feasibility checks

This provides a more robust solver that can scale.

## 3. ArgMax Decision Layer
After computing all candidate routes:
- Normalize all scores
- Compute: `score = alpha * cost + beta * speed + gamma * reliability`
- Select the optimal route using ArgMax

**Example output:**
```
Route 1 (solver output):
USD to USDC (via CoinGecko price + FX rate)
USDC to Polygon (via LI.FI bridge)
Polygon to India offramp (via Onmeta/Transak)
Offramp to INR (via bank rail fee table)
Cost: 0.52 percent
ETA: 1.8 hours
Reliability: 4.7 out of 5
```

**Note:** The example route demonstrates the optimization capabilities. Actual route segments are generated from the integrated APIs listed above, with cost, latency, and reliability scores computed from real-time data.

