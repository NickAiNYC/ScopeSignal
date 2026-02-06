"""
Insurance Limits Validator

Validates contractor insurance coverage against agency-specific requirements.
Different NYC agencies (SCA, DDC, HPD, etc.) have different insurance thresholds.
"""

from typing import Dict, List, Optional
from datetime import datetime


class InsuranceValidator:
    """
    Validates insurance coverage against agency requirements.
    
    Agency-specific insurance requirements for NYC construction:
    - SCA (School Construction Authority): Higher limits due to school environments
    - DDC (Department of Design and Construction): Standard city project limits
    - HPD (Housing Preservation and Development): Residential project limits
    - DEP (Department of Environmental Protection): Infrastructure project limits
    - NYCHA (NYC Housing Authority): Public housing limits
    """
    
    # Standard insurance requirements by agency (in millions)
    AGENCY_REQUIREMENTS = {
        "SCA": {
            "general_liability": 2.0,  # $2M per occurrence
            "auto_liability": 1.0,     # $1M combined single limit
            "workers_comp": "statutory",
            "umbrella": 5.0            # $5M umbrella policy
        },
        "DDC": {
            "general_liability": 1.0,
            "auto_liability": 1.0,
            "workers_comp": "statutory",
            "umbrella": 2.0
        },
        "HPD": {
            "general_liability": 1.0,
            "auto_liability": 1.0,
            "workers_comp": "statutory",
            "umbrella": 2.0
        },
        "DEP": {
            "general_liability": 2.0,
            "auto_liability": 1.0,
            "workers_comp": "statutory",
            "umbrella": 3.0
        },
        "NYCHA": {
            "general_liability": 1.0,
            "auto_liability": 1.0,
            "workers_comp": "statutory",
            "umbrella": 2.0
        },
        "default": {
            "general_liability": 1.0,
            "auto_liability": 1.0,
            "workers_comp": "statutory",
            "umbrella": 2.0
        }
    }
    
    def __init__(self):
        """Initialize insurance validator"""
        pass
    
    def validate_coverage(
        self,
        user_coverage: Dict[str, float],
        agency: str,
        trade: Optional[str] = None
    ) -> Dict:
        """
        Validate user's insurance coverage against agency requirements.
        
        Args:
            user_coverage: Dict with coverage amounts (in millions)
                          e.g., {"general_liability": 2.0, "umbrella": 5.0}
            agency: Agency code (e.g., "SCA", "DDC")
            trade: Optional trade type (may affect requirements)
        
        Returns:
            Dict with validation result:
            {
                "compliant": bool,
                "missing_coverage": List[str],
                "insufficient_limits": Dict[str, dict],
                "details": str
            }
        """
        agency_upper = agency.upper()
        requirements = self.AGENCY_REQUIREMENTS.get(
            agency_upper,
            self.AGENCY_REQUIREMENTS["default"]
        )
        
        missing_coverage = []
        insufficient_limits = {}
        
        for coverage_type, required_amount in requirements.items():
            # Skip workers comp as it's always "statutory"
            if required_amount == "statutory":
                if coverage_type not in user_coverage or user_coverage[coverage_type] == 0:
                    missing_coverage.append(coverage_type)
                continue
            
            # Check if coverage exists
            if coverage_type not in user_coverage:
                missing_coverage.append(coverage_type)
                continue
            
            # Check if coverage is sufficient
            user_amount = user_coverage.get(coverage_type, 0)
            if user_amount < required_amount:
                insufficient_limits[coverage_type] = {
                    "required": required_amount,
                    "current": user_amount,
                    "shortfall": required_amount - user_amount
                }
        
        compliant = len(missing_coverage) == 0 and len(insufficient_limits) == 0
        
        # Build details message
        if compliant:
            details = f"All insurance requirements met for {agency_upper}"
        else:
            details_parts = []
            if missing_coverage:
                details_parts.append(f"Missing coverage: {', '.join(missing_coverage)}")
            if insufficient_limits:
                limits_msgs = [
                    f"{ct}: need ${req['required']}M, have ${req['current']}M"
                    for ct, req in insufficient_limits.items()
                ]
                details_parts.append(f"Insufficient limits: {'; '.join(limits_msgs)}")
            details = ". ".join(details_parts)
        
        return {
            "compliant": compliant,
            "missing_coverage": missing_coverage,
            "insufficient_limits": insufficient_limits,
            "details": details,
            "agency": agency_upper,
            "requirements": requirements
        }
    
    def get_agency_requirements(self, agency: str) -> Dict:
        """
        Get insurance requirements for a specific agency.
        
        Args:
            agency: Agency code
        
        Returns:
            Dict of insurance requirements
        """
        agency_upper = agency.upper()
        return self.AGENCY_REQUIREMENTS.get(
            agency_upper,
            self.AGENCY_REQUIREMENTS["default"]
        )
