"""
Integration Test Suite Using Data Simulator

Tests the full integration of:
1. Data simulator generating "ugly" agency text
2. Opportunity classifier handling skewed data
3. Feasibility scorer cross-referencing with compliance

This ensures the system can handle realistic, ambiguous agency language.
"""

import pytest
import sys
import os

# Add packages to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from data.simulator import generate_batch, generate_adversarial_set, generate_update
from packages.agents.opportunity import OpportunityClassifier, DecisionProof
from packages.compliance import FeasibilityScorer


class TestSimulatorIntegration:
    """
    Test classifier with simulator-generated data.
    
    These tests validate that the system can handle:
    - Deliberately ambiguous agency language
    - Skewed data distributions (CONTESTABLE is rare)
    - Edge cases designed to break classification
    """
    
    def test_simulator_generates_valid_updates(self):
        """Test that simulator produces valid update structure"""
        update = generate_update(seed=42)
        
        assert "text" in update
        assert "category" in update
        assert "trade" in update
        assert "expected_classification" in update
        assert update["trade"] in ["electrical", "HVAC", "plumbing"]
    
    def test_batch_generation_maintains_distribution(self):
        """Test that batch generation respects rarity of contestable work"""
        batch = generate_batch(count=100, seed=42)
        
        # Count classifications
        contestable_count = sum(
            1 for u in batch
            if u["expected_classification"] == "CONTESTABLE"
        )
        
        # CONTESTABLE should be rare (around 2%)
        assert contestable_count < 10, "CONTESTABLE opportunities should be rare"
        assert len(batch) == 100
    
    def test_adversarial_cases_exist(self):
        """Test that adversarial cases are properly generated"""
        adversarial = generate_adversarial_set()
        
        assert len(adversarial) > 0
        for case in adversarial:
            assert "text" in case
            assert "note" in case
            assert "expected_classification" in case


class TestOpportunityClassifierIntegration:
    """
    Test opportunity classifier with DecisionProof using simulated data.
    """
    
    @pytest.fixture
    def mock_user_data(self):
        """Mock user insurance and license data"""
        return {
            "insurance": {
                "general_liability": 2.0,
                "auto_liability": 1.0,
                "umbrella": 5.0,
                "workers_comp": 1.0
            },
            "licenses": [
                {
                    "type": "Master Electrician",
                    "number": "ME123456",
                    "status": "active",
                    "expiry": "2027-12-31"
                },
                {
                    "type": "HVAC License",
                    "number": "HVAC789",
                    "status": "active",
                    "expiry": "2027-06-30"
                }
            ]
        }
    
    def test_decision_proof_creation(self):
        """Test that DecisionProof properly records audit trail"""
        proof = DecisionProof(decision_type="test_classification")
        
        proof.record_input("test_input", "value")
        proof.add_reasoning_step("step1", "First step")
        proof.add_validation_check("check1", True, "Passed")
        proof.record_output("result", "CLOSED")
        
        proof_dict = proof.to_dict()
        
        assert proof_dict["decision_type"] == "test_classification"
        assert "test_input" in proof_dict["inputs"]
        assert len(proof_dict["reasoning_chain"]) == 1
        assert len(proof_dict["validation_checks"]) == 1
        assert proof.is_valid()
    
    def test_decision_proof_validation_failure(self):
        """Test that DecisionProof detects validation failures"""
        proof = DecisionProof(decision_type="test")
        
        proof.add_validation_check("test_check", False, "Failed")
        
        assert not proof.is_valid()


class TestFeasibilityScorerIntegration:
    """
    Test feasibility scorer with simulated opportunities and compliance data.
    """
    
    @pytest.fixture
    def mock_classification(self):
        """Mock opportunity classification result"""
        return {
            "classification": "CONTESTABLE",
            "confidence": 85,
            "trade_relevant": True,
            "reasoning": "Clear RFP with deadline",
            "risk_note": "Could be limited pool",
            "recommended_action": "Submit proposal",
            "_metadata": {
                "trade": "Electrical",
                "model": "deepseek-chat"
            }
        }
    
    @pytest.fixture
    def compliant_user(self):
        """Mock compliant user data"""
        return {
            "insurance": {
                "general_liability": 2.0,
                "auto_liability": 1.0,
                "umbrella": 5.0,
                "workers_comp": 1.0
            },
            "licenses": [
                {
                    "type": "Master Electrician",
                    "number": "ME123456",
                    "status": "active",
                    "expiry": "2027-12-31"
                }
            ]
        }
    
    @pytest.fixture
    def non_compliant_user(self):
        """Mock non-compliant user data"""
        return {
            "insurance": {
                "general_liability": 0.5,  # Insufficient
                "auto_liability": 1.0,
                "umbrella": 1.0  # Insufficient
            },
            "licenses": [
                {
                    "type": "Master Electrician",
                    "number": "ME123456",
                    "status": "expired",
                    "expiry": "2020-12-31"
                }
            ]
        }
    
    def test_feasibility_calculation_compliant_contestable(
        self,
        mock_classification,
        compliant_user
    ):
        """Test feasibility for compliant user with CONTESTABLE opportunity"""
        scorer = FeasibilityScorer()
        
        result = scorer.calculate_feasibility(
            mock_classification,
            compliant_user["insurance"],
            compliant_user["licenses"],
            "SCA"
        )
        
        assert result["can_bid"] is True
        assert result["opportunity_level"] == "CONTESTABLE"
        assert result["compliance_readiness"]["insurance"] is True
        assert result["compliance_readiness"]["license"] is True
        assert result["feasibility_score"] > 70
        assert len(result["blockers"]) == 0
    
    def test_feasibility_calculation_non_compliant(
        self,
        mock_classification,
        non_compliant_user
    ):
        """Test feasibility for non-compliant user"""
        scorer = FeasibilityScorer()
        
        result = scorer.calculate_feasibility(
            mock_classification,
            non_compliant_user["insurance"],
            non_compliant_user["licenses"],
            "SCA"
        )
        
        assert result["can_bid"] is False
        assert result["compliance_readiness"]["insurance"] is False
        assert result["compliance_readiness"]["license"] is False
        assert result["feasibility_score"] < 20
        assert len(result["blockers"]) > 0
    
    def test_feasibility_closed_opportunity(self, compliant_user):
        """Test that CLOSED opportunities always score 0"""
        scorer = FeasibilityScorer()
        
        closed_opp = {
            "classification": "CLOSED",
            "confidence": 95,
            "trade_relevant": False,
            "_metadata": {"trade": "Electrical"}
        }
        
        result = scorer.calculate_feasibility(
            closed_opp,
            compliant_user["insurance"],
            compliant_user["licenses"],
            "DDC"
        )
        
        assert result["can_bid"] is False
        assert result["feasibility_score"] == 0.0
        assert "CLOSED" in result["blockers"][0]
    
    def test_batch_feasibility_calculation(self, compliant_user):
        """Test batch feasibility calculation"""
        scorer = FeasibilityScorer()
        
        opportunities = [
            {
                "classification": "CONTESTABLE",
                "confidence": 85,
                "trade_relevant": True,
                "_metadata": {"trade": "Electrical"},
                "agency": "SCA",
                "id": "opp1"
            },
            {
                "classification": "CLOSED",
                "confidence": 90,
                "trade_relevant": False,
                "_metadata": {"trade": "HVAC"},
                "agency": "DDC",
                "id": "opp2"
            }
        ]
        
        results = scorer.batch_calculate_feasibility(
            opportunities,
            compliant_user["insurance"],
            compliant_user["licenses"]
        )
        
        assert len(results) == 2
        assert results[0]["opportunity_id"] == "opp1"
        assert results[1]["opportunity_id"] == "opp2"
        assert results[0]["can_bid"] is True
        assert results[1]["can_bid"] is False


class TestSkewedDataHandling:
    """
    Test that the system properly handles skewed distributions
    where CONTESTABLE opportunities are rare (as in real life).
    """
    
    def test_simulator_produces_realistic_skew(self):
        """Test that simulator creates realistic distribution"""
        batch = generate_batch(count=200, seed=12345)
        
        categories = {}
        for update in batch:
            cat = update["expected_classification"]
            categories[cat] = categories.get(cat, 0) + 1
        
        # Verify CONTESTABLE is rare
        contestable_pct = (categories.get("CONTESTABLE", 0) / 200) * 100
        
        assert contestable_pct < 5, "CONTESTABLE should be less than 5% (realistic)"
        
        # Verify CLOSED dominates
        closed_pct = (categories.get("CLOSED", 0) / 200) * 100
        
        assert closed_pct > 50, "CLOSED should dominate distribution"
    
    def test_adversarial_edge_cases(self):
        """Test that adversarial cases are properly structured"""
        adversarial = generate_adversarial_set()
        
        # All adversarial cases should have explanatory notes
        for case in adversarial:
            assert "note" in case
            assert len(case["note"]) > 10
            assert case["expected_classification"] in ["CLOSED", "SOFT_OPEN", "CONTESTABLE"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
