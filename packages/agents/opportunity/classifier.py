"""
Opportunity Classifier with DecisionProof Audit Trail

Wraps the original ScopeSignal classifier with audit trail capabilities.
Maintains the skeptical-by-default philosophy while providing full traceability.
"""

import sys
import os
from typing import Dict, Literal, Optional

# Add parent directory to path to import classifier
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from classifier.agent import ScopeSignalClassifier, SYSTEM_PROMPT, ClassificationError
from .decision_proof import DecisionProof


class OpportunityClassifier:
    """
    Conservative opportunity classifier with DecisionProof audit trail.
    
    Wraps ScopeSignal's core classification logic with comprehensive
    audit trail capabilities, maintaining the skeptical-by-default
    philosophy while providing full traceability for compliance purposes.
    """
    
    def __init__(self, api_key: str = None, max_retries: int = 3, enable_cache: bool = True):
        """
        Initialize classifier with audit trail capabilities.
        
        Args:
            api_key: DeepSeek API key (or from environment)
            max_retries: Maximum retry attempts for classification
            enable_cache: Whether to enable result caching
        """
        self.classifier = ScopeSignalClassifier(
            api_key=api_key,
            max_retries=max_retries,
            enable_cache=enable_cache
        )
    
    def classify_with_proof(
        self,
        update_text: str,
        trade: Literal["Electrical", "HVAC", "Plumbing"],
        agency: Optional[str] = None
    ) -> tuple[Dict, DecisionProof]:
        """
        Classify opportunity with full audit trail.
        
        Args:
            update_text: Raw text from agency notice
            trade: One of "Electrical", "HVAC", "Plumbing"
            agency: Optional agency identifier (e.g., "SCA", "DDC")
        
        Returns:
            Tuple of (classification_result, decision_proof)
        """
        # Initialize decision proof
        proof = DecisionProof(decision_type="opportunity_classification")
        
        # Record inputs
        proof.record_input("update_text", update_text)
        proof.record_input("trade", trade)
        if agency:
            proof.record_input("agency", agency)
        
        proof.add_reasoning_step(
            "initialization",
            f"Starting classification for {trade} opportunity"
        )
        
        try:
            # Perform classification
            result = self.classifier.classify_update(update_text, trade)
            
            # Record reasoning steps from classification
            proof.add_reasoning_step(
                "trade_relevance_check",
                f"Trade relevant: {result['trade_relevant']}"
            )
            
            proof.add_reasoning_step(
                "classification_decision",
                f"Classification: {result['classification']} (confidence: {result['confidence']}%)"
            )
            
            proof.add_reasoning_step(
                "reasoning",
                result['reasoning']
            )
            
            proof.add_reasoning_step(
                "risk_assessment",
                result['risk_note']
            )
            
            # Record outputs
            proof.record_output("classification", result['classification'])
            proof.record_output("confidence", result['confidence'])
            proof.record_output("trade_relevant", result['trade_relevant'])
            proof.record_output("reasoning", result['reasoning'])
            proof.record_output("risk_note", result['risk_note'])
            proof.record_output("recommended_action", result['recommended_action'])
            
            # Add validation checks
            proof.add_validation_check(
                "trade_classification_consistency",
                result['trade_relevant'] or result['classification'] == 'CLOSED',
                "Trade-irrelevant updates must be classified as CLOSED"
            )
            
            proof.add_validation_check(
                "confidence_range",
                0 <= result['confidence'] <= 100,
                f"Confidence must be 0-100, got {result['confidence']}"
            )
            
            proof.add_validation_check(
                "classification_valid",
                result['classification'] in ['CLOSED', 'SOFT_OPEN', 'CONTESTABLE'],
                f"Valid classification received: {result['classification']}"
            )
            
            # Add skepticism validation
            if result['classification'] == 'CONTESTABLE':
                proof.add_validation_check(
                    "contestable_confidence_ceiling",
                    result['confidence'] <= 85,
                    "CONTESTABLE classifications maintain skeptical confidence ceiling"
                )
            
            # Add metadata
            if '_metadata' in result:
                for key, value in result['_metadata'].items():
                    proof.add_metadata(key, value)
            
            proof.add_metadata("skeptical_by_default", True)
            proof.add_metadata("system_prompt_hash", hash(SYSTEM_PROMPT))
            
            return result, proof
            
        except ClassificationError as e:
            proof.add_reasoning_step(
                "classification_error",
                f"Classification failed: {str(e)}"
            )
            proof.add_validation_check(
                "classification_success",
                False,
                str(e)
            )
            raise
        except Exception as e:
            proof.add_reasoning_step(
                "unexpected_error",
                f"Unexpected error: {str(e)}"
            )
            proof.add_validation_check(
                "classification_success",
                False,
                str(e)
            )
            raise
    
    def classify_without_proof(
        self,
        update_text: str,
        trade: Literal["Electrical", "HVAC", "Plumbing"]
    ) -> Dict:
        """
        Classify without audit trail (legacy compatibility).
        
        Args:
            update_text: Raw text from agency notice
            trade: One of "Electrical", "HVAC", "Plumbing"
        
        Returns:
            Classification result dictionary
        """
        return self.classifier.classify_update(update_text, trade)


def classify_opportunity(
    update_text: str,
    trade: Literal["Electrical", "HVAC", "Plumbing"],
    api_key: str = None,
    with_proof: bool = True,
    agency: Optional[str] = None
):
    """
    Convenience function for one-off classifications with optional audit trail.
    
    Args:
        update_text: Raw text from agency notice
        trade: One of "Electrical", "HVAC", "Plumbing"
        api_key: Optional API key override
        with_proof: Whether to return DecisionProof
        agency: Optional agency identifier
    
    Returns:
        Classification result, or tuple of (result, proof) if with_proof=True
    """
    classifier = OpportunityClassifier(api_key=api_key)
    
    if with_proof:
        return classifier.classify_with_proof(update_text, trade, agency)
    else:
        return classifier.classify_without_proof(update_text, trade)
