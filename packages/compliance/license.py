"""
Trade License Validator

Validates contractor trade licenses against work requirements.
NYC requires specific licenses for different trade work.
"""

from typing import Dict, List, Optional
from datetime import datetime


class LicenseValidator:
    """
    Validates trade licenses against work requirements.
    
    NYC trade license categories:
    - Master Electrician
    - Master Plumber
    - Master Fire Suppression Piping Contractor
    - HVAC License (various types)
    - General Contractor License
    """
    
    # Map trades to required license types
    TRADE_LICENSE_REQUIREMENTS = {
        "Electrical": ["Master Electrician", "Electrical Contractor"],
        "Plumbing": ["Master Plumber", "Plumbing Contractor"],
        "HVAC": ["HVAC License", "Mechanical Contractor"],
    }
    
    def __init__(self):
        """Initialize license validator"""
        pass
    
    def validate_license(
        self,
        user_licenses: List[Dict],
        trade: str,
        work_description: Optional[str] = None
    ) -> Dict:
        """
        Validate user's licenses for specific trade work.
        
        Args:
            user_licenses: List of license dicts with:
                          [{"type": str, "number": str, "status": str, "expiry": str}]
            trade: Trade type (e.g., "Electrical", "HVAC", "Plumbing")
            work_description: Optional work description for specialized requirements
        
        Returns:
            Dict with validation result:
            {
                "compliant": bool,
                "active_licenses": List[str],
                "expired_licenses": List[str],
                "missing_licenses": List[str],
                "details": str
            }
        """
        required_license_types = self.TRADE_LICENSE_REQUIREMENTS.get(trade, [])
        
        if not required_license_types:
            return {
                "compliant": False,
                "active_licenses": [],
                "expired_licenses": [],
                "missing_licenses": [],
                "details": f"Unknown trade: {trade}"
            }
        
        active_licenses = []
        expired_licenses = []
        
        today = datetime.utcnow().date()
        
        for license_info in user_licenses:
            license_type = license_info.get("type", "")
            status = license_info.get("status", "").lower()
            expiry = license_info.get("expiry", "")
            
            # Check if license type matches requirements
            if not any(req in license_type for req in required_license_types):
                continue
            
            # Check expiry date
            is_expired = False
            if expiry:
                try:
                    expiry_date = datetime.fromisoformat(expiry.replace('Z', '+00:00')).date()
                    is_expired = expiry_date < today
                except:
                    pass
            
            # Check status
            if status == "active" and not is_expired:
                active_licenses.append(license_type)
            else:
                expired_licenses.append(license_type)
        
        # Determine missing licenses
        has_required = len(active_licenses) > 0
        missing_licenses = [] if has_required else required_license_types
        
        compliant = has_required
        
        # Build details message
        if compliant:
            details = f"Active {trade} license found: {', '.join(active_licenses)}"
        else:
            if expired_licenses:
                details = f"Expired licenses: {', '.join(expired_licenses)}. "
            else:
                details = ""
            details += f"Required: {' or '.join(required_license_types)}"
        
        return {
            "compliant": compliant,
            "active_licenses": active_licenses,
            "expired_licenses": expired_licenses,
            "missing_licenses": missing_licenses,
            "details": details,
            "trade": trade
        }
    
    def get_trade_requirements(self, trade: str) -> List[str]:
        """
        Get license requirements for a specific trade.
        
        Args:
            trade: Trade type
        
        Returns:
            List of required license types
        """
        return self.TRADE_LICENSE_REQUIREMENTS.get(trade, [])
