"""
Conservative Opportunity Classifier Agent
Migrated from ScopeSignal's classifier module.
Maintains skeptical-by-default philosophy with DecisionProof audit trails.
"""

from .classifier import OpportunityClassifier, classify_opportunity
from .decision_proof import DecisionProof

__all__ = ['OpportunityClassifier', 'classify_opportunity', 'DecisionProof']
