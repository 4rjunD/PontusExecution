"""
Kraken API Client
Handles cryptocurrency exchange operations via Kraken API
"""
import httpx
import hmac
import hashlib
import base64
import time
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode

from app.clients.base_client import BaseClient
from app.schemas.route_segment import RouteSegment, SegmentType
from app.config import settings

logger = logging.getLogger(__name__)


class KrakenClient(BaseClient):
    """Kraken API client for cryptocurrency operations"""
    
    BASE_URL = "https://api.kraken.com"
    
    def __init__(self, client: httpx.AsyncClient):
        super().__init__(client)
        self.api_key = settings.kraken_api_key
        self.private_key = settings.kraken_private_key
        
        if not self.api_key or not self.private_key:
            logger.warning("Kraken API credentials not configured")
    
    def _sign_message(self, url_path: str, data: Dict[str, Any]) -> str:
        """
        Sign a message using Kraken's API signature method
        
        Args:
            url_path: API endpoint path (e.g., "/0/private/Balance")
            data: Request data as dictionary
        """
        if not self.private_key:
            raise ValueError("Kraken private key not configured")
        
        # Create nonce
        nonce = str(int(time.time() * 1000))
        data["nonce"] = nonce
        
        # Encode data
        post_data = urlencode(data)
        encoded = (str(data["nonce"]) + post_data).encode()
        message = url_path.encode() + hashlib.sha256(encoded).digest()
        
        # Decode private key
        secret = base64.b64decode(self.private_key)
        
        # Create signature
        signature = hmac.new(secret, message, hashlib.sha512)
        sigdigest = base64.b64encode(signature.digest())
        
        return sigdigest.decode()
    
    def _get_headers(self, url_path: str, data: Dict[str, Any]) -> Dict[str, str]:
        """Get authentication headers for Kraken API"""
        if not self.api_key:
            raise ValueError("Kraken API key not configured")
        
        signature = self._sign_message(url_path, data)
        return {
            "API-Key": self.api_key,
            "API-Sign": signature
        }
    
    async def get_account_balance(self) -> Dict[str, float]:
        """Get account balance for all assets"""
        if not self.api_key or not self.private_key:
            return {}
        
        try:
            url_path = "/0/private/Balance"
            url = f"{self.BASE_URL}{url_path}"
            data = {}
            
            headers = self._get_headers(url_path, data)
            
            response = await self.client.post(
                url,
                headers=headers,
                data=data,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("error"):
                logger.error(f"Kraken API error: {result['error']}")
                return {}
            
            return result.get("result", {})
        except Exception as e:
            logger.error(f"Error fetching Kraken balance: {e}")
            return {}
    
    async def get_ticker(self, pair: str) -> Optional[Dict[str, Any]]:
        """
        Get ticker information for a trading pair
        
        Args:
            pair: Trading pair (e.g., "XBTUSD", "ETHUSD")
        """
        try:
            url = f"{self.BASE_URL}/0/public/Ticker"
            params = {"pair": pair}
            
            response = await self.client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            result = response.json()
            
            if result.get("error"):
                logger.error(f"Kraken API error: {result['error']}")
                return None
            
            # Kraken returns data with pair name as key
            pair_data = list(result.get("result", {}).values())
            return pair_data[0] if pair_data else None
        except Exception as e:
            logger.error(f"Error fetching Kraken ticker: {e}")
            return None
    
    async def get_asset_pairs(self) -> Dict[str, Any]:
        """Get all available trading pairs"""
        try:
            url = f"{self.BASE_URL}/0/public/AssetPairs"
            response = await self.client.get(url, timeout=10.0)
            response.raise_for_status()
            result = response.json()
            
            if result.get("error"):
                logger.error(f"Kraken API error: {result['error']}")
                return {}
            
            return result.get("result", {})
        except Exception as e:
            logger.error(f"Error fetching Kraken asset pairs: {e}")
            return {}
    
    async def create_order(
        self,
        pair: str,
        type: str,  # "buy" or "sell"
        ordertype: str,  # "market", "limit", etc.
        volume: Optional[float] = None,
        price: Optional[float] = None,
        amount: Optional[float] = None  # For market orders, amount in quote currency
    ) -> Optional[Dict[str, Any]]:
        """
        Create a trading order
        
        Args:
            pair: Trading pair (e.g., "XBTUSD")
            type: "buy" or "sell"
            ordertype: "market" or "limit"
            volume: Order volume in base currency
            price: Limit price (required for limit orders)
            amount: Amount in quote currency (for market buy orders)
        """
        if not self.api_key or not self.private_key:
            raise ValueError("Kraken API credentials not configured")
        
        try:
            url_path = "/0/private/AddOrder"
            url = f"{self.BASE_URL}{url_path}"
            
            data = {
                "pair": pair,
                "type": type,
                "ordertype": ordertype
            }
            
            if ordertype == "market" and type == "buy" and amount:
                # Market buy: specify amount in quote currency
                data["oflags"] = "fcib"  # Fee in base currency
                # For market buy, we need to calculate volume from amount
                # This is a simplification - in production, you'd want to get current price first
                data["volume"] = str(amount)  # Kraken accepts this for market orders
            elif volume:
                data["volume"] = str(volume)
            
            if price:
                data["price"] = str(price)
            
            headers = self._get_headers(url_path, data)
            
            response = await self.client.post(
                url,
                headers=headers,
                data=data,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("error"):
                error_msg = result["error"]
                logger.error(f"Kraken API error creating order: {error_msg}")
                raise ValueError(f"Kraken API error: {error_msg}")
            
            return result.get("result", {})
        except Exception as e:
            logger.error(f"Error creating Kraken order: {e}")
            raise
    
    async def get_order_status(self, txid: str) -> Optional[Dict[str, Any]]:
        """Get status of an order"""
        if not self.api_key or not self.private_key:
            return None
        
        try:
            url_path = "/0/private/QueryOrders"
            url = f"{self.BASE_URL}{url_path}"
            
            data = {
                "txid": txid,
                "trades": True
            }
            
            headers = self._get_headers(url_path, data)
            
            response = await self.client.post(
                url,
                headers=headers,
                data=data,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("error"):
                logger.error(f"Kraken API error: {result['error']}")
                return None
            
            orders = result.get("result", {})
            return orders.get(txid) if orders else None
        except Exception as e:
            logger.error(f"Error fetching Kraken order status: {e}")
            return None
    
    async def cancel_order(self, txid: str) -> Optional[Dict[str, Any]]:
        """
        Cancel an order
        
        Args:
            txid: Transaction ID (order ID) to cancel
        """
        if not self.api_key or not self.private_key:
            return None
        
        try:
            url_path = "/0/private/CancelOrder"
            url = f"{self.BASE_URL}{url_path}"
            
            data = {
                "txid": txid
            }
            
            headers = self._get_headers(url_path, data)
            
            response = await self.client.post(
                url,
                headers=headers,
                data=data,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("error"):
                error_msg = result["error"]
                logger.error(f"Kraken API error cancelling order: {error_msg}")
                return None
            
            return result.get("result", {})
        except Exception as e:
            logger.error(f"Error cancelling Kraken order: {e}")
            return None
    
    async def modify_order(self, txid: str, new_volume: Optional[float] = None, new_price: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Modify an order (cancel old, create new)
        
        Args:
            txid: Transaction ID to modify
            new_volume: New volume (for limit orders)
            new_price: New price (for limit orders)
        """
        if not self.api_key or not self.private_key:
            return None
        
        try:
            # Get current order
            order = await self.get_order_status(txid)
            if not order:
                raise ValueError("Order not found")
            
            # If order is already filled, cannot modify
            if order.get("status") == "closed":
                raise ValueError("Cannot modify filled order")
            
            # Cancel old order
            cancel_result = await self.cancel_order(txid)
            if not cancel_result:
                raise ValueError("Failed to cancel order")
            
            # Return info for creating new order
            return {
                "cancelled_order_id": txid,
                "can_create_new": True,
                "old_order": order
            }
        except Exception as e:
            logger.error(f"Error modifying Kraken order: {e}")
            return None
    
    async def execute_crypto_swap(
        self,
        from_asset: str,
        to_asset: str,
        amount: float
    ) -> Dict[str, Any]:
        """
        Execute a crypto swap (buy/sell order)
        
        Args:
            from_asset: Source asset (e.g., "USD", "BTC", "ETH")
            to_asset: Target asset (e.g., "USD", "BTC", "ETH")
            amount: Amount in from_asset
        
        Returns:
            Dict with order details
        """
        if not self.api_key or not self.private_key:
            raise ValueError("Kraken API credentials not configured")
        
        # Map assets to Kraken symbols
        asset_map = {
            "USD": "USD",
            "USDT": "USDT",
            "USDC": "USDC",
            "BTC": "XBT",  # Kraken uses XBT for Bitcoin
            "ETH": "ETH",
            "EUR": "EUR",
            "GBP": "GBP"
        }
        
        from_kraken = asset_map.get(from_asset.upper(), from_asset.upper())
        to_kraken = asset_map.get(to_asset.upper(), to_asset.upper())
        
        # Determine trading pair
        # Common pairs: XBTUSD, ETHUSD, etc.
        if from_kraken == "USD" and to_kraken in ["XBT", "ETH", "USDT", "USDC"]:
            pair = f"{to_kraken}USD"
            order_type = "buy"
        elif to_kraken == "USD" and from_kraken in ["XBT", "ETH", "USDT", "USDC"]:
            pair = f"{from_kraken}USD"
            order_type = "sell"
            # For sell, volume is in base currency
            volume = amount
        else:
            # Try direct pair
            pair = f"{from_kraken}{to_kraken}"
            order_type = "buy"  # Default, may need adjustment
        
        # Create market order
        order_result = await self.create_order(
            pair=pair,
            type=order_type,
            ordertype="market",
            volume=volume if order_type == "sell" else None,
            amount=amount if order_type == "buy" else None
        )
        
        if not order_result:
            raise ValueError("Failed to create Kraken order")
        
        txid = order_result.get("txid", [None])[0] if order_result.get("txid") else None
        
        return {
            "order_id": txid,
            "pair": pair,
            "type": order_type,
            "status": "pending",
            "created_at": time.time(),
            "kraken_response": order_result
        }
    
    async def fetch_segments(self) -> List[RouteSegment]:
        """
        Fetch crypto segments from Kraken
        Gets current prices for major trading pairs
        """
        segments = []
        
        if not self.api_key:
            return segments
        
        # Common trading pairs to fetch
        pairs = [
            ("BTC", "USD", "XBTUSD"),
            ("ETH", "USD", "ETHUSD"),
            ("USDT", "USD", "USDTUSD"),
            ("USDC", "USD", "USDCUSD"),
        ]
        
        for from_asset, to_asset, kraken_pair in pairs:
            try:
                ticker = await self.get_ticker(kraken_pair)
                if ticker:
                    # Get current price (last trade price)
                    price = float(ticker.get("c", [0])[0]) if ticker.get("c") else None
                    
                    if price:
                        # Calculate fee (Kraken typically charges 0.16-0.26% for maker/taker)
                        fee_percent = 0.2  # Average fee
                        
                        segments.append(self.normalize_segment(
                            segment_type=SegmentType.CRYPTO,
                            from_asset=from_asset,
                            to_asset=to_asset,
                            cost={
                                "fee_percent": fee_percent,
                                "fixed_fee": 0.0,
                                "effective_fx_rate": price if from_asset == "USD" else 1.0 / price
                            },
                            latency={"min_minutes": 1, "max_minutes": 5},
                            reliability_score=0.95,
                            provider="kraken"
                        ))
            except Exception as e:
                logger.debug(f"Error fetching Kraken ticker for {kraken_pair}: {e}")
                continue
        
        return segments

