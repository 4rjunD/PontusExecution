# Pontus User Frontend

Frontend application for the Pontus Execution Layer API - Multi-rail payment routing and execution dashboard.

## Features

### A. Core Product (Money Routing & Execution)
- ✅ AI-powered multi-rail payment routing
- ✅ Real-time optimization across cost, speed, reliability, and liquidity
- ✅ Delegated execution (Wise/Nium/exchange accounts)
- ✅ Simulation mode (testnet swaps, bridges, off-ramps)
- ✅ Route comparison engine
- ✅ Per-transaction audit trail

### B. Treasury Automation
- ✅ Unified balance view across all rails
- ✅ Automated rebalancing
- ✅ Cash positioning analysis
- ✅ Global liquidity dashboard

### C. Global Payout OS
- ✅ One-click vendor/contractor payments
- ✅ Upload invoice + AI validation
- ✅ Batch payouts (CSV upload)
- ✅ Smart batching across recipients

### D. FX Intelligence & Cost Optimization
- ✅ Real-time FX monitoring (20+ sources)
- ✅ Predictive cost forecasting
- ✅ Optimal time to send recommendations
- ✅ Micro-hedging with stablecoins

### E. Compliance & Controls
- ✅ Automatic invoice validation
- ✅ Corridor-based rule enforcement
- ✅ Suspicious pattern detection
- ✅ Full audit logs
- ✅ Role-based access control (RBAC)

### F. Reconciliation & Accounting Automation
- ✅ Automatic payment → invoice matching
- ✅ FX delta tracking
- ✅ Multi-rail ledger
- ✅ Export to QuickBooks, Xero, NetSuite

### G. Analytics & Reporting
- ✅ Savings dashboard
- ✅ Cost breakdown by corridor/provider/asset/chain
- ✅ Speed/reliability heatmaps
- ✅ Monthly forecasting
- ✅ Historical performance insights

### H. Integrations & Connectivity
- ✅ Wise Business
- ✅ Kraken
- ✅ Nium
- ✅ Transak, Onmeta
- ✅ Socket, LI.FI bridges
- ✅ 0x, Uniswap liquidity

### I. Developer Platform
- ✅ API documentation
- ✅ Webhook configuration
- ✅ Sandbox mode
- ✅ Route graph introspection

## Tech Stack

- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components
- **Radix UI** - Accessible primitives
- **Recharts** - Data visualization
- **Axios** - API client

## Getting Started

### Prerequisites

- Node.js 18+ 
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Environment Variables

Create a `.env.local` file:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project Structure

```
app/
  dashboard/          # Dashboard pages
    routing/         # Route optimization & execution
    treasury/        # Treasury management
    payouts/         # Global payout OS
    fx/              # FX intelligence
    compliance/      # Compliance & controls
    reconciliation/  # Reconciliation & accounting
    analytics/       # Analytics & reporting
    integrations/    # Integrations
    developer/       # Developer platform
components/
  dashboard/         # Dashboard-specific components
  ui/                # Reusable UI components
lib/
  api.ts            # API client functions
  utils.ts          # Utility functions
```

## API Integration

All API calls are made through the `lib/api.ts` file which connects to the backend at `http://localhost:8000`.

### Available API Functions

- `healthCheck()` - Check API health
- `getRouteSegments()` - Get available route segments
- `optimizeRoute()` - Optimize payment route
- `executeRoute()` - Execute payment route
- `getExecutionStatus()` - Get execution status
- `getExecutionHistory()` - Get execution history
- And more...

## Features Implemented

✅ Dashboard with collapsible sidebar
✅ Sales Tracker component
✅ Gantt chart for task management
✅ All feature pages (A-I)
✅ API integration
✅ Responsive design
✅ Real-time data updates

## Next Steps

1. Add more data visualization charts
2. Implement real-time WebSocket updates
3. Add more advanced filtering and search
4. Enhance mobile responsiveness
5. Add user authentication

## License

Private - Pontus Execution Layer
