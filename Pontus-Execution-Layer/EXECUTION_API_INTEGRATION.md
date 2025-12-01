# Execution API Integration - Wise & Kraken

## Overview

The execution layer has been enhanced to support **real API execution** alongside simulation mode. This allows the system to execute actual transfers via Wise Business API and crypto swaps via Kraken API.

## Configuration

### Environment Variables

Credentials are stored in `.env` file (not committed to git):

```bash
# Execution Layer API Keys
WISE_API_KEY=your_wise_api_key
WISE_API_EMAIL=your_wise_email
KRAKEN_API_KEY=your_kraken_api_key
KRAKEN_PRIVATE_KEY=your_kraken_private_key

# Execution Mode: "simulation" or "real"
EXECUTION_MODE=simulation
```

### Execution Modes

1. **Simulation Mode** (default): All executions are simulated - no real money moves
2. **Real Mode**: Executions use actual APIs when available (Wise for FX/bank rails, Kraken for crypto)

## API Clients

### Wise Business API Client (`app/clients/wise_client.py`)

**Features:**
- Get profiles and accounts
- Create quotes for FX conversions
- Create and fund transfers
- Check transfer status

**Methods:**
- `get_profiles()` - Get all Wise profiles
- `get_accounts(profile_id)` - Get balance accounts
- `create_quote(profile_id, source_currency, target_currency, amount)` - Create transfer quote
- `create_transfer(quote_id, target_account, reference)` - Create transfer from quote
- `fund_transfer(transfer_id)` - Actually execute the transfer
- `execute_bank_transfer(...)` - Complete transfer workflow

**Usage:**
```python
from app.clients import WiseClient
import httpx

client = httpx.AsyncClient()
wise = WiseClient(client)

# Get profiles
profiles = await wise.get_profiles()

# Create quote
quote = await wise.create_quote(
    profile_id=profiles[0]["id"],
    source_currency="USD",
    target_currency="EUR",
    source_amount=1000.0
)

# Execute transfer
transfer = await wise.execute_bank_transfer(
    from_currency="USD",
    to_currency="EUR",
    amount=1000.0,
    target_account_details={"account_id": "..."},
    profile_id=profiles[0]["id"]
)
```

### Kraken API Client (`app/clients/kraken_client.py`)

**Features:**
- Get account balances
- Get ticker prices
- Create market/limit orders
- Check order status
- Execute crypto swaps

**Methods:**
- `get_account_balance()` - Get all asset balances
- `get_ticker(pair)` - Get current price for trading pair
- `create_order(pair, type, ordertype, volume, price)` - Create trading order
- `get_order_status(txid)` - Check order status
- `execute_crypto_swap(from_asset, to_asset, amount)` - Execute swap

**Usage:**
```python
from app.clients import KrakenClient
import httpx

client = httpx.AsyncClient()
kraken = KrakenClient(client)

# Get balance
balance = await kraken.get_account_balance()

# Execute swap
swap_result = await kraken.execute_crypto_swap(
    from_asset="USD",
    to_asset="BTC",
    amount=1000.0
)

# Check order status
status = await kraken.get_order_status(swap_result["order_id"])
```

## Execution Layer Integration

### Segment Executors

The segment executors now support both simulation and real execution:

1. **FXExecutor** - Uses Wise API for real FX conversions
2. **CryptoExecutor** - Uses Kraken API for real crypto swaps
3. **BankRailExecutor** - Uses Wise API for real bank transfers

### How It Works

1. **Check Execution Mode**: Executors check `settings.execution_mode`
2. **API Availability**: If mode is "real" and API client is available, use real API
3. **Fallback**: If real execution fails, automatically falls back to simulation
4. **Logging**: All execution attempts (real or simulated) are logged

### Example Flow

```python
# In ExecutionService
executor = FXExecutor(simulator, wise_client=wise_client)

# Executor checks:
if self.execution_mode == "real" and self.wise_client:
    # Execute via Wise API
    result = await self.wise_client.create_quote(...)
else:
    # Fall back to simulation
    result = await self.simulator.simulate_fx_conversion(...)
```

## API Endpoints

### Execute Route (POST /api/routes/execute)

The existing execution endpoint now supports real execution when:
- `EXECUTION_MODE=real` in environment
- API credentials are configured
- Route segments use supported providers (Wise, Kraken)

**Request:**
```json
{
  "from_asset": "USD",
  "to_asset": "EUR",
  "amount": 1000.0,
  "from_network": null,
  "to_network": null
}
```

**Response:**
```json
{
  "execution_id": "...",
  "status": "completed",
  "route": [...],
  "segment_executions": [
    {
      "segment_type": "fx",
      "status": "completed",
      "simulation_data": {
        "execution_mode": "real",
        "quote_id": "...",
        "type": "wise_fx_conversion"
      }
    }
  ]
}
```

## Security Considerations

1. **Credentials**: Never commit `.env` file to git
2. **Sandbox Mode**: Wise client supports sandbox for testing
3. **Error Handling**: All API errors are caught and logged
4. **Fallback**: System always falls back to simulation if real execution fails
5. **Validation**: All amounts and parameters are validated before API calls

## Testing

### Test Simulation Mode
```bash
EXECUTION_MODE=simulation python -m app.main
```

### Test Real Mode (with caution!)
```bash
EXECUTION_MODE=real python -m app.main
```

**Warning**: Real mode will execute actual transfers. Use sandbox/test accounts first!

## Next Steps

1. **Add More Providers**: Integrate additional exchanges and payment rails
2. **Order Management**: Add order tracking and status polling
3. **Error Recovery**: Implement retry logic for failed API calls
4. **Webhooks**: Add webhook support for async status updates
5. **Audit Trail**: Enhanced logging for compliance

## Documentation Links

- [Wise API Docs](https://docs.wise.com/guides/developer/auth-and-security)
- [Kraken API Docs](https://docs.kraken.com/rest/)

## Support

For issues or questions:
1. Check API documentation
2. Review logs for error messages
3. Verify credentials are correct
4. Ensure execution mode is set correctly

