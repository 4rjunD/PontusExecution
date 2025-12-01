import json
import os
from typing import Dict, Any, List
from app.clients.base_client import BaseClient
from app.schemas.route_segment import RouteSegment


class RegulatoryClient(BaseClient):
    """Loads regulatory constraints from local JSON file"""
    
    def __init__(self, client=None):
        # Regulatory client doesn't need HTTP client
        # Create a dummy client if None
        if client is None:
            import httpx
            client = httpx.AsyncClient()
        super().__init__(client)
        self.constraints: Dict[str, Any] = {}
        self._load_constraints()
    
    def _load_constraints(self):
        """Load regulatory constraints from JSON file"""
        constraints_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "data",
            "regulatory_constraints.json"
        )
        
        # Create default constraints if file doesn't exist
        default_constraints = {
            "restricted_pairs": [
                {"from": "USD", "to": "CNY", "reason": "capital_controls"},
                {"from": "USD", "to": "RUB", "reason": "sanctions"},
            ],
            "max_amounts": {
                "USD": 10000,
                "EUR": 10000,
            },
            "required_kyc": ["USD", "EUR", "GBP"],
            "blocked_countries": ["KP", "IR", "SY"],
            "network_restrictions": {
                "tornado_cash": {"blocked": True},
            }
        }
        
        try:
            if os.path.exists(constraints_path):
                with open(constraints_path, "r") as f:
                    self.constraints = json.load(f)
            else:
                # Create directory and file with defaults
                os.makedirs(os.path.dirname(constraints_path), exist_ok=True)
                with open(constraints_path, "w") as f:
                    json.dump(default_constraints, f, indent=2)
                self.constraints = default_constraints
        except Exception as e:
            self.constraints = default_constraints
    
    async def fetch_segments(self) -> List[RouteSegment]:
        """Regulatory client doesn't fetch segments, just provides constraints"""
        return []
    
    def get_constraints(self) -> Dict[str, Any]:
        """Get regulatory constraints"""
        return self.constraints
    
    def is_allowed(self, from_asset: str, to_asset: str, amount: float = None) -> bool:
        """Check if a route is allowed by regulatory constraints"""
        # Check restricted pairs
        restricted = self.constraints.get("restricted_pairs", [])
        for pair in restricted:
            if pair["from"] == from_asset and pair["to"] == to_asset:
                return False
        
        # Check max amounts
        if amount:
            max_amounts = self.constraints.get("max_amounts", {})
            if from_asset in max_amounts and amount > max_amounts[from_asset]:
                return False
        
        return True

