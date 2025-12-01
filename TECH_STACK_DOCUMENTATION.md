# 📚 Pontus Tech Stack - Complete Documentation

**Last Updated:** November 23, 2025  
**Version:** 3.0.0

---

## 📋 Table of Contents

1. [Backend Architecture](#backend-architecture)
2. [Frontend Architecture](#frontend-architecture)
3. [Infrastructure & DevOps](#infrastructure--devops)
4. [External APIs & Integrations](#external-apis--integrations)
5. [Future Components](#future-components)
6. [Development Tools](#development-tools)

---

## 🏗️ Backend Architecture

### **A. Data Layer (Route Intelligence Layer)**

**Purpose:** Continuously ingest real-time pricing, liquidity, and fee data from multiple sources

#### Core Framework
- **FastAPI** `0.104.1` - Modern, fast web framework for building APIs
- **Uvicorn** `0.24.0` - ASGI server with standard extensions
- **Python** `3.8+` - Programming language

#### HTTP & Networking
- **httpx** `0.25.2` - Async HTTP client for API calls
- **aioredis** `2.0.1` - Async Redis client
- **asyncpg** `0.29.0` - Async PostgreSQL driver

#### Data Validation & Serialization
- **Pydantic** `2.5.0` - Data validation using Python type annotations
- **Pydantic Settings** `2.1.0` - Settings management using Pydantic models

#### Database & ORM
- **PostgreSQL** `15.15` - Primary relational database
- **SQLAlchemy** `2.0.23` - Python SQL toolkit and ORM
- **Alembic** `1.12.1` - Database migration tool
- **psycopg2-binary** `2.9.9` - PostgreSQL adapter (sync)

#### Caching
- **Redis** `8.4.0` - In-memory data store for caching
- **redis** `5.0.1` - Python Redis client

#### Data Clients (Adapters)
- **FXClient** - Fetches FX rates from:
  - Frankfurter API (free)
  - ExchangeRate API (free/demo)
  - ECB (European Central Bank)
- **CryptoClient** - Fetches crypto prices from:
  - CoinGecko API (free)
  - Exchange public endpoints
- **GasClient** - Fetches gas fees from:
  - Etherscan API
  - Polygonscan API
  - BSCScan API
  - Snowscan API
  - Arbiscan API
  - Optimism API
- **BridgeClient** - Fetches bridge quotes from:
  - Socket API
  - LI.FI API
- **RampClient** - Fetches on/off-ramp quotes from:
  - Transak API (demo)
  - Onmeta API (test)
- **BankRailClient** - Estimates bank rail fees from:
  - Wise calculator
  - Remitly calculators
  - Hard-coded fee tables
- **LiquidityClient** - Fetches liquidity data from:
  - 0x API
  - Uniswap subgraphs
- **RegulatoryClient** - Loads regulatory constraints from:
  - Local JSON file (`data/regulatory_constraints.json`)

#### Background Tasks
- **asyncio** - Native Python async/await for concurrent operations
- Custom background task scheduler for:
  - Fast refresh (2s): Crypto prices, gas fees, bridge quotes
  - Slow refresh (30-60s): FX rates, bank rails, liquidity data
  - Full refresh (60s): Complete snapshot of all segments

#### Rate Limiting & Security
- **slowapi** `0.1.9` - Rate limiting middleware
- Custom API key authentication middleware
- CORS middleware (configurable origins)

---

### **B. Routing Engine (Core Optimizer)**

**Purpose:** Generate cheapest, fastest, most reliable routes using formal optimization

#### Optimization Solvers
- **OR-Tools** `9.9.3963` - Google's optimization library
  - Shortest path algorithms
  - Multi-weight path finding
  - Constraint-based routing
  - Multi-objective optimization
  - Graceful fallback if not installed

- **IBM CPLEX** (Optional) - Advanced optimization solver
  - Mixed-integer programming (MIP)
  - Cost/latency tradeoff modeling
  - Reliability-weighted constraints
  - Strict feasibility checks
  - Auto-detects if installed, falls back to OR-Tools

#### Mathematical Computing
- **NumPy** `1.24.3` - Numerical computing library
  - Matrix operations
  - Statistical calculations
  - Array manipulations

#### Decision Layer
- **ArgMax Decision Algorithm** (Custom)
  - Normalizes cost, speed, reliability
  - Weighted score: `alpha * cost + beta * speed + gamma * reliability`
  - Selects optimal route using ArgMax
  - Returns top K routes

#### Graph Building
- **Custom Graph Builder** - Converts route segments to graph structure
  - Nodes: Assets/networks
  - Edges: Route segments
  - Weighted edges (cost, latency, reliability)
  - Constraint handling

---

### **C. Execution Layer**

**Purpose:** Execute selected routes in simulation or real accounts

#### Execution Framework
- **Custom Execution Service** - Orchestrates route execution
- **Segment Executors** - Handlers for specific segment types:
  - `FXExecutor` - FX conversions
  - `CryptoExecutor` - Crypto swaps
  - `BridgeExecutor` - Cross-chain bridges
  - `RampExecutor` - On/off-ramps
  - `BankRailExecutor` - Bank transfers

#### Real API Integration
- **Wise Business API Client** - Real FX and bank transfers
  - Profile management
  - Quote creation
  - Transfer creation
  - Automatic funding
  - Transfer modification
  - Transfer cancellation
- **Kraken API Client** - Real crypto swaps
  - Ticker data
  - Account balance
  - Order creation
  - Order modification
  - Order cancellation

#### Simulation
- **Custom Simulator** - Simulates execution without real money
  - Testnet wallet generation
  - Balance simulation
  - Transaction simulation
  - Confirmation tracking

#### Advanced Features
- **Pause/Resume** - Control execution flow
- **Dynamic Re-routing** - AI-based route changes during execution
- **Parallel Execution** - Execute independent segments concurrently
- **Transaction Modification** - Modify in-flight transactions
- **Cancellation** - Cancel pending transactions

---

### **D. Treasury Management System**

**Purpose:** Unified treasury system with automated rebalancing

#### Treasury Services
- **Unified Balance Aggregation** - Aggregates across all sources
- **Rebalancing Engine** - Automated asset rebalancing
- **Cash Positioning** - Optimal allocation recommendations
- **Payout Forecasting** - 30-day forecast with route optimization
- **Approval Workflows** - Multi-level approval system
- **Vendor Whitelisting** - Automated approval for trusted vendors
- **Anomaly Detection** - Pattern-based fraud detection
- **Audit Logging** - Complete action-level audit trail

#### API Endpoints
- `/api/treasury/balances` - Unified balances
- `/api/treasury/fx-rates` - Real-time FX rates
- `/api/treasury/gas-prices` - Gas prices
- `/api/treasury/liquidity` - Liquidity data
- `/api/treasury/rebalancing-rules` - Rebalancing rules
- `/api/treasury/cash-positioning` - Recommendations
- `/api/treasury/payout-forecast` - Forecasts
- `/api/treasury/optimal-time` - Optimal timing
- `/api/treasury/corridor-liquidity` - Corridor analysis

---

### **E. FX Intelligence System**

**Purpose:** Real-time FX monitoring and cost optimization

#### FX Services
- **Live Rate Aggregation** - Real-time rates from multiple sources
- **Optimal Time Calculator** - AI-powered timing recommendations
- **Cost Forecasting** - Predictive cost analysis
- **Rate Comparison** - Compare rates across providers
- **Historical Analysis** - Rate history and volatility
- **Micro-Hedging** - Stablecoin hedging strategies

#### API Endpoints
- `/api/fx/rates` - Live FX rates
- `/api/fx/rates/{pair}/history` - Historical data
- `/api/fx/optimal-time` - Optimal time recommendations
- `/api/fx/cost-forecast` - Cost forecasting
- `/api/fx/micro-hedge` - Hedging position
- `/api/fx/sources` - Active sources
- `/api/fx/compare` - Rate comparison

---

## 🎨 Frontend Architecture

### **Core Framework**
- **Next.js** `16.0.3` - React framework with SSR/SSG
- **React** `18.3.0` - UI library
- **React DOM** `18.3.0` - React DOM renderer
- **TypeScript** `5.4.0` - Type-safe JavaScript

### **Styling & UI**
- **Tailwind CSS** `3.4.1` - Utility-first CSS framework
- **Tailwind Animate** `1.0.7` - Animation utilities
- **PostCSS** `8.4.33` - CSS processing
- **Autoprefixer** `10.4.17` - CSS vendor prefixing

### **UI Component Library**
- **shadcn/ui** - Reusable component library built on:
  - **Radix UI** - Headless UI primitives:
    - `@radix-ui/react-avatar` `1.1.11`
    - `@radix-ui/react-checkbox` `1.3.3`
    - `@radix-ui/react-dialog` `1.1.15`
    - `@radix-ui/react-dropdown-menu` `2.1.16`
    - `@radix-ui/react-label` `2.1.8`
    - `@radix-ui/react-popover` `1.1.15`
    - `@radix-ui/react-select` `2.2.6`
    - `@radix-ui/react-separator` `1.1.8`
    - `@radix-ui/react-slot` `1.0.2`
    - `@radix-ui/react-switch` `1.2.6`
    - `@radix-ui/react-tabs` `1.0.4`
    - `@radix-ui/react-tooltip` `1.0.7`

### **Icons & Graphics**
- **Lucide React** `0.344.0` - Icon library
- **Next/Image** - Optimized image component

### **Forms & Validation**
- **React Hook Form** `7.50.1` - Form state management
- **Zod** `3.22.4` - Schema validation
- **@hookform/resolvers** `3.3.4` - Form validation resolvers

### **Data Visualization**
- **Recharts** `2.15.4` - Charting library for:
  - Savings dashboards
  - Cost breakdowns
  - Performance heatmaps
  - Historical insights

### **HTTP Client**
- **Axios** `1.6.7` - Promise-based HTTP client

### **Utilities**
- **clsx** `2.1.0` - Conditional class names
- **tailwind-merge** `2.2.0` - Merge Tailwind classes
- **class-variance-authority** `0.7.0` - Component variants
- **date-fns** `3.6.0` - Date utility library

### **Development Tools**
- **ESLint** `8.56.0` - Code linting
- **ESLint Config Next** `14.2.0` - Next.js ESLint config
- **TypeScript Types**:
  - `@types/node` `20.11.0`
  - `@types/react` `18.2.0`
  - `@types/react-dom` `18.2.0`

### **Frontend Features**
- **Dashboard with Collapsible Sidebar** - Navigation component
- **Sales Tracker** - Sales analytics component
- **Gantt Chart** - Task management visualization
- **Real-time Data Updates** - Auto-refresh every 5 seconds
- **Responsive Design** - Mobile-first approach

---

## 🗄️ Infrastructure & DevOps

### **Database**
- **PostgreSQL** `15.15`
  - Primary data store
  - Route segments persistence
  - Snapshot storage
  - Audit logs (future)
  - User data (future)

### **Caching**
- **Redis** `8.4.0`
  - Route segment caching (2s TTL)
  - Session storage (future)
  - Rate limiting storage
  - Real-time data cache

### **Containerization** (Optional)
- **Docker** - Container runtime
- **Docker Compose** - Multi-container orchestration
  - PostgreSQL container
  - Redis container

### **Process Management**
- **Homebrew Services** (macOS) - Service management
  - PostgreSQL service
  - Redis service

### **Deployment** (Future)
- **Production Server**: TBD
- **CDN**: TBD (for static assets)
- **Load Balancer**: TBD
- **Monitoring**: TBD (Prometheus, Grafana)

---

## 🔌 External APIs & Integrations

### **FX Rate Providers**
- **Frankfurter API** - Free FX rates
- **ExchangeRate API** - Free/demo FX rates
- **ECB** - European Central Bank rates

### **Crypto Data**
- **CoinGecko API** - Crypto prices
- **Exchange APIs** - Public endpoints

### **Blockchain Data**
- **Etherscan API** - Ethereum gas fees
- **Polygonscan API** - Polygon gas fees
- **BSCScan API** - BSC gas fees
- **Snowscan API** - Avalanche gas fees
- **Arbiscan API** - Arbitrum gas fees
- **Optimism API** - Optimism gas fees

### **Bridge Aggregators**
- **Socket API** - Cross-chain bridge quotes
- **LI.FI API** - Bridge aggregation

### **On/Off-Ramp**
- **Transak API** - On/off-ramp quotes (demo)
- **Onmeta API** - On/off-ramp quotes (test)

### **Liquidity Providers**
- **0x API** - DEX liquidity
- **Uniswap Subgraphs** - Uniswap liquidity data

### **Bank Rails**
- **Wise Business API** - Real FX and bank transfers
- **Remitly** - Bank rail estimates (calculator)

### **Crypto Exchanges**
- **Kraken API** - Real crypto swaps
- **Binance** (Future) - Exchange integration
- **OKX** (Future) - Exchange integration

---

## 🚀 Future Components

### **A. Agentic Execution System** (Planned)

**Purpose:** Automated browser-based execution with delegated access

#### Planned Technologies
- **Selenium** / **Playwright** - Browser automation
- **Puppeteer** (Alternative) - Headless Chrome automation
- **Credential Management System**:
  - Encrypted credential storage
  - Multi-provider support
  - Credential rotation
  - Access control

#### Features
- Automated login to Wise/Nium/exchanges
- Form filling and submission
- Invoice upload and validation
- Payment initiation
- Confirmation tracking
- Full audit trail

---

### **B. Compliance & Controls** (Enhanced)

**Purpose:** Advanced compliance features

#### Planned Technologies
- **Machine Learning** (Future):
  - Anomaly detection models
  - Pattern recognition
  - Fraud detection
- **Rule Engine**:
  - Corridor-based rules
  - Custom business rules
  - Regulatory compliance checks

#### Features
- Automatic invoice validation
- Suspicious pattern detection
- RBAC (Role-Based Access Control)
- Full audit logs
- Compliance reporting

---

### **C. Reconciliation & Accounting** (Enhanced)

**Purpose:** Automated reconciliation and accounting integration

#### Planned Technologies
- **Accounting API Integrations**:
  - QuickBooks API
  - Xero API
  - NetSuite API
- **Matching Algorithms**:
  - Payment-to-invoice matching
  - FX delta tracking
  - Multi-rail ledger

#### Features
- Automatic payment matching
- FX delta tracking
- Multi-rail ledger
- Export to accounting formats
- Reconciliation reports

---

### **D. Analytics & Reporting** (Enhanced)

**Purpose:** Advanced analytics and insights

#### Planned Technologies
- **Analytics Engine**:
  - Time-series database (InfluxDB/TimescaleDB)
  - Data aggregation pipelines
- **Visualization**:
  - Enhanced Recharts
  - D3.js (for complex visualizations)
  - Custom dashboards

#### Features
- Savings dashboard
- Cost breakdown by corridor/provider/asset/chain
- Speed/reliability heatmaps
- Monthly forecasting
- Historical insights
- Custom reports

---

### **E. Developer Platform** (Enhanced)

**Purpose:** API and developer tools

#### Planned Technologies
- **API Gateway** (Future):
  - Kong / AWS API Gateway
  - Rate limiting per API key
  - Usage analytics
- **Webhook System**:
  - Webhook delivery service
  - Retry logic
  - Signature verification
- **Sandbox Mode**:
  - Test environment
  - Mock data
  - Simulation mode

#### Features
- RESTful API
- Webhook notifications
- Sandbox environment
- API documentation (OpenAPI/Swagger)
- Route graph introspection
- Developer dashboard

---

### **F. Global Payout OS** (Enhanced)

**Purpose:** One-click vendor, contractor, supplier payments

#### Planned Technologies
- **Invoice Processing**:
  - OCR (Optical Character Recognition)
  - AI/ML for invoice parsing
  - Validation engine
- **Batch Processing**:
  - CSV/Excel parsing
  - Bulk payment processing
  - Smart batching algorithms

#### Features
- Invoice upload and validation
- Batch payouts (CSV/API)
- Smart batching across recipients
- One-click payments
- Payment scheduling

---

## 🛠️ Development Tools

### **Version Control**
- **Git** - Source control
- **GitHub** - Repository hosting

### **Package Management**
- **pip** - Python package manager
- **npm** / **yarn** - Node.js package manager

### **Code Quality**
- **ESLint** - JavaScript/TypeScript linting
- **TypeScript** - Type checking
- **Pydantic** - Python data validation

### **Testing** (Future)
- **pytest** - Python testing framework
- **Jest** - JavaScript testing framework
- **React Testing Library** - React component testing
- **Playwright** - End-to-end testing

### **Documentation**
- **Markdown** - Documentation format
- **OpenAPI/Swagger** - API documentation
- **JSDoc** - JavaScript documentation
- **Sphinx** (Future) - Python documentation

---

## 📊 Data Flow Architecture

### **Current Flow**
```
External APIs → Data Clients → Aggregator Service → Redis Cache → PostgreSQL
                                                      ↓
                                              Routing Service → Optimization Solvers
                                                      ↓
                                              Execution Service → Real APIs / Simulator
                                                      ↓
                                              Frontend (Next.js) → User Dashboard
```

### **Future Flow** (With Agentic Execution)
```
External APIs → Data Clients → Aggregator Service → Redis Cache → PostgreSQL
                                                      ↓
                                              Routing Service → Optimization Solvers
                                                      ↓
                                              Execution Service → Agentic Browser → Real Accounts
                                                      ↓
                                              Frontend (Next.js) → User Dashboard
```

---

## 🔐 Security Stack

### **Current**
- API key authentication (optional)
- Rate limiting (per IP)
- CORS configuration
- Environment variable management
- Secure credential storage (future)

### **Future**
- OAuth 2.0 / JWT authentication
- Multi-factor authentication (MFA)
- Encryption at rest
- Encryption in transit (TLS/SSL)
- Secrets management (HashiCorp Vault / AWS Secrets Manager)
- Audit logging
- RBAC (Role-Based Access Control)

---

## 📈 Monitoring & Observability (Future)

### **Planned Technologies**
- **Prometheus** - Metrics collection
- **Grafana** - Metrics visualization
- **ELK Stack** (Elasticsearch, Logstash, Kibana) - Log aggregation
- **Sentry** - Error tracking
- **Datadog** / **New Relic** - APM (Application Performance Monitoring)

### **Metrics to Track**
- API response times
- Route calculation performance
- Execution success rates
- Cache hit rates
- Database query performance
- Error rates
- User activity

---

## 🌐 Deployment Architecture (Future)

### **Production Stack**
- **Cloud Provider**: AWS / GCP / Azure
- **Container Orchestration**: Kubernetes / Docker Swarm
- **Load Balancer**: NGINX / AWS ALB
- **CDN**: Cloudflare / AWS CloudFront
- **Database**: Managed PostgreSQL (RDS / Cloud SQL)
- **Cache**: Managed Redis (ElastiCache / Memorystore)
- **Message Queue**: RabbitMQ / AWS SQS (for async tasks)
- **File Storage**: S3 / GCS (for invoices, documents)

---

## 📝 Summary

### **Current Tech Stack**
- **Backend**: FastAPI, Python, PostgreSQL, Redis
- **Frontend**: Next.js, React, TypeScript, Tailwind CSS
- **Optimization**: OR-Tools, CPLEX (optional)
- **APIs**: 20+ external API integrations
- **Real Execution**: Wise Business, Kraken

### **Future Additions**
- Browser automation (Selenium/Playwright)
- ML/AI for anomaly detection
- Accounting integrations (QuickBooks, Xero, NetSuite)
- Enhanced analytics (time-series DB)
- Webhook system
- Advanced monitoring (Prometheus, Grafana)
- Cloud deployment (Kubernetes, managed services)

---

**Document Version:** 1.0  
**Last Updated:** November 23, 2025

