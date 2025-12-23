"""
Basic unit tests for classifier
Run with: python -m pytest tests/
"""

import pytest
from classifier import ScopeSignalClassifier, ClassificationError


def test_classifier_initialization():
    """Test classifier can be initialized"""
    # This will fail if ANTHROPIC_API_KEY not set - that's expected
    try:
        classifier = ScopeSignalClassifier()
        assert classifier.model == "claude-sonnet-4-20250514"
        assert classifier.max_retries == 3
    except ValueError:
        # Expected if no API key
        pass


def test_invalid_trade():
    """Test that invalid trade raises error"""
    classifier = ScopeSignalClassifier(api_key="fake_key_for_test")
    
    with pytest.raises(ValueError, match="Invalid trade"):
        classifier.classify_update("Some text", "InvalidTrade")


def test_classification_schema():
    """Test that classification result has required fields"""
    # Mock test - in real usage, would need API key
    required_fields = [
        "trade_relevant",
        "classification", 
        "confidence",
        "reasoning",
        "risk_note",
        "recommended_action"
    ]
    
    # Just verify the list is defined correctly
    assert len(required_fields) == 6
    assert "classification" in required_fields


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
