"""
Feasibility Scorer - Cross-Reference Opportunity with Compliance

Combines ScopeSignal opportunity classification with ConComplyAi compliance data
to produce a final "Feasibility Score" indicating whether a user can actually
bid on a classified opportunity.
"""

from typing import Dict, List, Optional
from .insurance import InsuranceValidator
from .license import LicenseValidator


class FeasibilityScorer:
    """
    Calculates feasibility scores for bidding opportunities.
    
    Combines:
    1. Opportunity classification (CLOSED/SOFT_OPEN/CONTESTABLE)
    2. Insurance compliance (agency-specific requirements)
    3. Trade license status (active and valid)
    
    Philosophy: Even a CONTESTABLE opportunity is worthless if you're
    not compliant to bid. This is the integration point between
    ScopeSignal and ConComplyAi.
    """
    
    def __init__(self):
        """Initialize feasibility scorer with validators"""
        self.insurance_validator = InsuranceValidator()
        self.license_validator = LicenseValidator()
    
    def calculate_feasibility(
        self,
        opportunity_classification: Dict,
        user_insurance: Dict[str, float],
        user_licenses: List[Dict],
        agency: str
    ) -> Dict:
        """
        Calculate comprehensive feasibility score.
        
        Args:
            opportunity_classification: Result from OpportunityClassifier
                                       Must include: classification, confidence, trade_relevant, trade
            user_insurance: User's insurance coverage (in millions)
            user_licenses: List of user's licenses
            agency: Agency code (e.g., "SCA", "DDC")
        
        Returns:
            Dict with:
            {
                "feasibility_score": float (0-100),
                "can_bid": bool,
                "opportunity_level": str,
                "compliance_readiness": Dict,
                "blockers": List[str],
                "recommendations": List[str],
                "details": Dict
            }
        """
        # Extract classification data
        classification = opportunity_classification.get("classification", "CLOSED")
        confidence = opportunity_classification.get("confidence", 0)
        trade_relevant = opportunity_classification.get("trade_relevant", False)
        trade = opportunity_classification.get("_metadata", {}).get("trade") or "Unknown"
        
        # Initialize result
        result = {
            "feasibility_score": 0.0,
            "can_bid": False,
            "opportunity_level": classification,
            "compliance_readiness": {
                "insurance": False,
                "license": False
            },
            "blockers": [],
            "recommendations": [],
            "details": {}
        }
        
        # Step 1: Check opportunity level
        if not trade_relevant or classification == "CLOSED":
            result["blockers"].append("Opportunity is CLOSED or not trade-relevant")
            result["recommendations"].append("Monitor for future updates")
            result["feasibility_score"] = 0.0
            result["details"]["opportunity_status"] = "No viable opportunity"
            return result
        
        # Step 2: Validate insurance
        insurance_result = self.insurance_validator.validate_coverage(
            user_insurance,
            agency,
            trade
        )
        
        result["compliance_readiness"]["insurance"] = insurance_result["compliant"]
        result["details"]["insurance"] = insurance_result
        
        if not insurance_result["compliant"]:
            result["blockers"].append(f"Insurance: {insurance_result['details']}")
            result["recommendations"].append("Update insurance coverage to meet agency requirements")
        
        # Step 3: Validate trade license
        license_result = self.license_validator.validate_license(
            user_licenses,
            trade
        )
        
        result["compliance_readiness"]["license"] = license_result["compliant"]
        result["details"]["license"] = license_result
        
        if not license_result["compliant"]:
            result["blockers"].append(f"License: {license_result['details']}")
            result["recommendations"].append("Obtain or renew required trade license")
        
        # Step 4: Calculate feasibility score
        # Base score from opportunity classification
        base_score = 0
        if classification == "CONTESTABLE":
            base_score = confidence  # Use full confidence for contestable
        elif classification == "SOFT_OPEN":
            base_score = confidence * 0.6  # Discount soft open opportunities
        
        # Apply compliance penalties
        compliance_multiplier = 1.0
        
        if not insurance_result["compliant"]:
            compliance_multiplier *= 0.3  # 70% penalty for missing insurance
        
        if not license_result["compliant"]:
            compliance_multiplier *= 0.2  # 80% penalty for missing license
        
        final_score = base_score * compliance_multiplier
        result["feasibility_score"] = round(final_score, 1)
        
        # Determine if user can bid
        # Must be CONTESTABLE or SOFT_OPEN, with both compliances met
        result["can_bid"] = (
            classification in ["CONTESTABLE", "SOFT_OPEN"] and
            insurance_result["compliant"] and
            license_result["compliant"]
        )
        
        # Add positive recommendations
        if result["can_bid"]:
            if classification == "CONTESTABLE":
                result["recommendations"].append("✓ You are compliant to bid - proceed with proposal")
            else:
                result["recommendations"].append("✓ You are compliant but opportunity is SOFT_OPEN - proceed with caution")
        
        # Add opportunity-specific recommendations
        if classification == "SOFT_OPEN" and result["can_bid"]:
            result["recommendations"].append("Research incumbent relationships before investing time")
        
        result["details"]["calculation"] = {
            "base_score": base_score,
            "compliance_multiplier": compliance_multiplier,
            "final_score": final_score
        }
        
        return result
    
    def batch_calculate_feasibility(
        self,
        opportunities: List[Dict],
        user_insurance: Dict[str, float],
        user_licenses: List[Dict]
    ) -> List[Dict]:
        """
        Calculate feasibility for multiple opportunities.
        
        Args:
            opportunities: List of opportunity classifications (must include 'agency' key)
            user_insurance: User's insurance coverage
            user_licenses: User's licenses
        
        Returns:
            List of feasibility results
        """
        results = []
        
        for opp in opportunities:
            agency = opp.get("agency", "DDC")  # Default to DDC
            
            feasibility = self.calculate_feasibility(
                opp,
                user_insurance,
                user_licenses,
                agency
            )
            
            # Add opportunity ID if present
            if "id" in opp:
                feasibility["opportunity_id"] = opp["id"]
            
            results.append(feasibility)
        
        return results


def check_feasibility(
    opportunity_classification: Dict,
    user_insurance: Dict[str, float],
    user_licenses: List[Dict],
    agency: str
) -> Dict:
    """
    Convenience function for single feasibility check.
    
    Args:
        opportunity_classification: Result from OpportunityClassifier
        user_insurance: User's insurance coverage
        user_licenses: User's licenses
        agency: Agency code
    
    Returns:
        Feasibility result dict
    """
    scorer = FeasibilityScorer()
    return scorer.calculate_feasibility(
        opportunity_classification,
        user_insurance,
        user_licenses,
        agency
    )
