"""
DecisionProof - Audit Trail for Opportunity Classifications

Provides the same audit trail mechanism used for compliance checks,
now applied to opportunity classifications. Maintains full traceability
of classification decisions and their reasoning.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json


class DecisionProof:
    """
    Audit trail for classification decisions.
    
    Records all inputs, outputs, and intermediate reasoning to support
    review and compliance verification. Aligned with ConComplyAi's
    existing audit trail approach.
    """
    
    def __init__(self, decision_type: str):
        """
        Initialize a new decision proof.
        
        Args:
            decision_type: Type of decision (e.g., 'opportunity_classification')
        """
        self.decision_type = decision_type
        self.timestamp = datetime.utcnow().isoformat()
        self.inputs: Dict[str, Any] = {}
        self.outputs: Dict[str, Any] = {}
        self.reasoning_chain: List[Dict[str, str]] = []
        self.metadata: Dict[str, Any] = {}
        self.validation_checks: List[Dict[str, Any]] = []
    
    def record_input(self, key: str, value: Any) -> None:
        """Record an input parameter"""
        self.inputs[key] = value
    
    def record_output(self, key: str, value: Any) -> None:
        """Record an output value"""
        self.outputs[key] = value
    
    def add_reasoning_step(self, step: str, detail: str) -> None:
        """
        Add a step in the reasoning chain.
        
        Args:
            step: Name of the reasoning step
            detail: Detailed explanation
        """
        self.reasoning_chain.append({
            "step": step,
            "detail": detail,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def add_validation_check(self, check_name: str, passed: bool, message: str = "") -> None:
        """
        Record a validation check result.
        
        Args:
            check_name: Name of the validation check
            passed: Whether the check passed
            message: Additional details
        """
        self.validation_checks.append({
            "check": check_name,
            "passed": passed,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the decision proof"""
        self.metadata[key] = value
    
    def to_dict(self) -> Dict:
        """Convert decision proof to dictionary"""
        return {
            "decision_type": self.decision_type,
            "timestamp": self.timestamp,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "reasoning_chain": self.reasoning_chain,
            "validation_checks": self.validation_checks,
            "metadata": self.metadata
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert decision proof to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, default=str)
    
    def is_valid(self) -> bool:
        """Check if all validation checks passed"""
        return all(check["passed"] for check in self.validation_checks)
