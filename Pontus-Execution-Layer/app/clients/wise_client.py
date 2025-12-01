"""
Wise Business API Client
Handles bank rail transfers and FX conversions via Wise Business API
"""
import httpx
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.clients.base_client import BaseClient
from app.schemas.route_segment import RouteSegment, SegmentType
from app.config import settings

logger = logging.getLogger(__name__)


class WiseClient(BaseClient):
    """Wise Business API client for bank rail transfers"""
    
    BASE_URL = "https://api.wise.com"
    SANDBOX_URL = "https://api.sandbox.transferwise.tech"
    
    def __init__(self, client: httpx.AsyncClient):
        super().__init__(client)
        self.api_key = settings.wise_api_key
        self.api_email = settings.wise_api_email
        self.use_sandbox = False  # Set to True for testing
        
        if not self.api_key:
            logger.warning("Wise API key not configured")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers for Wise API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        return headers
    
    def _get_base_url(self) -> str:
        """Get base URL (sandbox or production)"""
        return self.SANDBOX_URL if self.use_sandbox else self.BASE_URL
    
    async def get_profiles(self) -> List[Dict[str, Any]]:
        """Get all profiles associated with the API key"""
        if not self.api_key:
            return []
        
        try:
            url = f"{self._get_base_url()}/v1/profiles"
            response = await self.client.get(url, headers=self._get_headers(), timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching Wise profiles: {e}")
            return []
    
    async def get_accounts(self, profile_id: str) -> List[Dict[str, Any]]:
        """Get balance accounts for a profile"""
        if not self.api_key:
            return []
        
        try:
            url = f"{self._get_base_url()}/v2/profiles/{profile_id}/balances"
            response = await self.client.get(url, headers=self._get_headers(), timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching Wise accounts: {e}")
            return []
    
    async def create_quote(
        self,
        profile_id: str,
        source_currency: str,
        target_currency: str,
        source_amount: Optional[float] = None,
        target_amount: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a quote for a transfer
        
        Args:
            profile_id: Wise profile ID
            source_currency: Source currency code (e.g., "USD")
            target_currency: Target currency code (e.g., "EUR")
            source_amount: Amount in source currency (optional)
            target_amount: Amount in target currency (optional)
        """
        if not self.api_key:
            return None
        
        if not source_amount and not target_amount:
            raise ValueError("Either source_amount or target_amount must be provided")
        
        try:
            url = f"{self._get_base_url()}/v2/quotes"
            payload = {
                "profile": profile_id,
                "sourceCurrency": source_currency,
                "targetCurrency": target_currency
            }
            
            if source_amount:
                payload["sourceAmount"] = source_amount
            elif target_amount:
                payload["targetAmount"] = target_amount
            
            response = await self.client.post(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error creating Wise quote: {e}")
            return None
    
    async def create_transfer(
        self,
        quote_id: str,
        target_account: str,
        reference: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a transfer from a quote
        
        Args:
            quote_id: Quote ID from create_quote
            target_account: Target account ID or details
            reference: Optional reference for the transfer
        """
        if not self.api_key:
            return None
        
        try:
            url = f"{self._get_base_url()}/v1/transfers"
            payload = {
                "quoteUuid": quote_id,
                "targetAccount": target_account,
                "customerTransactionId": reference or f"pontus_{datetime.utcnow().isoformat()}"
            }
            
            response = await self.client.post(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error creating Wise transfer: {e}")
            return None
    
    async def fund_transfer(self, transfer_id: str, profile_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fund a transfer (actually execute it)
        
        Args:
            transfer_id: Transfer ID from create_transfer
            profile_id: Wise profile ID (will fetch if not provided)
        """
        if not self.api_key:
            return None
        
        try:
            if not profile_id:
                profiles = await self.get_profiles()
                if not profiles:
                    raise ValueError("No Wise profiles found")
                profile_id = profiles[0]["id"]
            
            url = f"{self._get_base_url()}/v3/profiles/{profile_id}/transfers/{transfer_id}/payments"
            payload = {
                "type": "BALANCE"
            }
            
            response = await self.client.post(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error funding Wise transfer: {e}")
            return None
    
    async def cancel_transfer(self, transfer_id: str) -> Optional[Dict[str, Any]]:
        """
        Cancel a transfer (if not yet funded)
        
        Args:
            transfer_id: Transfer ID to cancel
        """
        if not self.api_key:
            return None
        
        try:
            url = f"{self._get_base_url()}/v1/transfers/{transfer_id}/cancel"
            response = await self.client.put(
                url,
                headers=self._get_headers(),
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error cancelling Wise transfer: {e}")
            return None
    
    async def modify_transfer(self, transfer_id: str, new_amount: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Modify a transfer (create new quote and update transfer)
        
        Args:
            transfer_id: Transfer ID to modify
            new_amount: New amount (if different)
        """
        if not self.api_key:
            return None
        
        try:
            # Get current transfer
            transfer = await self.get_transfer_status(transfer_id)
            if not transfer:
                raise ValueError("Transfer not found")
            
            # If transfer is already funded, cannot modify
            if transfer.get("status") in ["outgoing_payment_sent", "funded", "processing"]:
                raise ValueError("Cannot modify funded transfer")
            
            # Cancel old transfer and create new one
            await self.cancel_transfer(transfer_id)
            
            # Return info for creating new transfer
            return {
                "cancelled_transfer_id": transfer_id,
                "can_create_new": True
            }
        except Exception as e:
            logger.error(f"Error modifying Wise transfer: {e}")
            return None
    
    async def get_transfer_status(self, transfer_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a transfer"""
        if not self.api_key:
            return None
        
        try:
            url = f"{self._get_base_url()}/v1/transfers/{transfer_id}"
            response = await self.client.get(url, headers=self._get_headers(), timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching Wise transfer status: {e}")
            return None
    
    def _get_profile_id(self) -> Optional[str]:
        """Get default profile ID (cached)"""
        # This should be cached after first call to get_profiles
        # For now, return None and let callers provide it
        return None
    
    async def execute_bank_transfer(
        self,
        from_currency: str,
        to_currency: str,
        amount: float,
        target_account_details: Dict[str, Any],
        profile_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a complete bank transfer via Wise
        
        Args:
            from_currency: Source currency
            to_currency: Target currency
            amount: Amount to transfer
            target_account_details: Target account information
            profile_id: Wise profile ID (will fetch if not provided)
        
        Returns:
            Dict with transfer details and status
        """
        if not self.api_key:
            raise ValueError("Wise API key not configured")
        
        # Get profile if not provided
        if not profile_id:
            profiles = await self.get_profiles()
            if not profiles:
                raise ValueError("No Wise profiles found")
            profile_id = profiles[0]["id"]
        
        # Create quote
        quote = await self.create_quote(
            profile_id=profile_id,
            source_currency=from_currency,
            target_currency=to_currency,
            source_amount=amount
        )
        
        if not quote:
            raise ValueError("Failed to create Wise quote")
        
        # Create transfer
        transfer = await self.create_transfer(
            quote_id=quote["id"],
            target_account=target_account_details.get("account_id") or str(target_account_details),
            reference=f"pontus_transfer_{datetime.utcnow().isoformat()}"
        )
        
        if not transfer:
            raise ValueError("Failed to create Wise transfer")
        
        return {
            "transfer_id": transfer.get("id"),
            "quote_id": quote.get("id"),
            "status": transfer.get("status"),
            "source_amount": quote.get("sourceAmount"),
            "target_amount": quote.get("targetAmount"),
            "fee": quote.get("fee"),
            "rate": quote.get("rate"),
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def fetch_segments(self) -> List[RouteSegment]:
        """
        Fetch bank rail segments from Wise
        Note: Wise doesn't provide public rate data, so we use hard-coded estimates
        This method can be used to validate API connectivity
        """
        segments = []
        
        if not self.api_key:
            return segments
        
        # Test API connectivity by fetching profiles
        try:
            profiles = await self.get_profiles()
            if profiles:
                logger.info(f"Wise API connected. Found {len(profiles)} profile(s)")
        except Exception as e:
            logger.warning(f"Wise API connectivity test failed: {e}")
        
        # Return empty segments - Wise rates are obtained via quotes, not public endpoints
        return segments

