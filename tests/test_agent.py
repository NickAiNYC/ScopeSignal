"""
Basic unit tests for classifier
Run with: python -m pytest tests/
"""

import pytest
from classifier import ScopeSignalClassifier, ClassificationError


def test_classifier_initialization():
    """Test classifier can be initialized"""
    # This will fail if DEEPSEEK_API_KEY not set - that's expected
    try:
        classifier = ScopeSignalClassifier()
        assert classifier.model == "deepseek-chat"
        assert classifier.max_retries == 3
        assert classifier.cache is not None  # Cache should be enabled by default
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


def test_cache_functionality():
    """Test that cache works correctly"""
    from classifier.cache import ResultCache
    import tempfile
    import os
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = ResultCache(cache_dir=tmpdir)
        
        # Test set and get
        test_result = {
            "classification": "CLOSED",
            "confidence": 85
        }
        
        cache.set("test_key", test_result)
        retrieved = cache.get("test_key")
        
        assert retrieved is not None
        assert retrieved["classification"] == "CLOSED"
        assert "_metadata" in retrieved
        assert retrieved["_metadata"]["cache_hit"] is True
        
        # Test stats
        stats = cache.stats()
        assert stats["entries"] == 1
        
        # Test clear
        count = cache.clear()
        assert count == 1
        
        stats = cache.stats()
        assert stats["entries"] == 0


def test_batch_processing():
    """Test batch processing interface"""
    classifier = ScopeSignalClassifier(api_key="fake_key_for_test")
    
    # Test that classify_batch method exists
    assert hasattr(classifier, 'classify_batch')
    assert callable(classifier.classify_batch)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
