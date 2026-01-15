"""
ScopeSignal Usage Examples
Demonstrates all major features with practical examples.
"""

from classifier import (
    ScopeSignalClassifier,
    classify_update,
    export_to_csv,
    export_to_json,
    export_summary_report
)
from evaluation import ClassificationMetrics


def example_1_single_classification():
    """Example 1: Classify a single update"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Single Classification")
    print("="*60 + "\n")
    
    result = classify_update(
        update_text="RFP issued for electrical work. Bids due March 15.",
        trade="Electrical"
    )
    
    print(f"Classification: {result['classification']}")
    print(f"Confidence: {result['confidence']}%")
    print(f"Reasoning: {result['reasoning']}")
    print(f"Recommended Action: {result['recommended_action']}")


def example_2_batch_processing():
    """Example 2: Process multiple updates"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Batch Processing")
    print("="*60 + "\n")
    
    classifier = ScopeSignalClassifier()
    
    updates = [
        {"text": "Amendment 2 issued. See Attachment B.", "trade": "Electrical"},
        {"text": "RFP posted for HVAC work.", "trade": "HVAC"},
        {"text": "Change order executed.", "trade": "Plumbing"},
    ]
    
    results = classifier.classify_batch(updates, show_progress=True)
    
    print(f"\nProcessed {len(results)} updates")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['classification']} (confidence: {result['confidence']}%)")


def example_3_export_results():
    """Example 3: Export results in multiple formats"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Export Results")
    print("="*60 + "\n")
    
    classifier = ScopeSignalClassifier()
    
    updates = [
        {"text": "Amendment issued", "trade": "Electrical"},
        {"text": "RFP posted", "trade": "HVAC"},
    ]
    
    results = classifier.classify_batch(updates, show_progress=False)
    
    # Export to CSV
    export_to_csv(results, "/tmp/results.csv", include_metadata=True)
    
    # Export to JSON
    export_to_json(results, "/tmp/results.json")
    
    # Generate summary report
    export_summary_report(results, "/tmp/summary.txt")
    
    print("Exported to /tmp/results.csv, /tmp/results.json, /tmp/summary.txt")


def example_4_cache_management():
    """Example 4: Cache management"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Cache Management")
    print("="*60 + "\n")
    
    classifier = ScopeSignalClassifier()
    
    # First call - cache miss
    result1 = classifier.classify_update("Amendment 2 issued", "Electrical")
    print(f"First call - Cache hit: {result1.get('_metadata', {}).get('cache_hit', False)}")
    
    # Second call - cache hit
    result2 = classifier.classify_update("Amendment 2 issued", "Electrical")
    print(f"Second call - Cache hit: {result2.get('_metadata', {}).get('cache_hit', False)}")
    
    # Check cache stats
    stats = classifier.cache.stats()
    print(f"\nCache entries: {stats['entries']}")
    print(f"Cache size: {stats['size_bytes']} bytes")


def example_5_enhanced_metrics():
    """Example 5: Enhanced metrics and analysis"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Enhanced Metrics")
    print("="*60 + "\n")
    
    # Sample results with expected classifications
    results = [
        {"actual": "CLOSED", "expected": "CLOSED", "confidence": 95},
        {"actual": "CLOSED", "expected": "CLOSED", "confidence": 90},
        {"actual": "SOFT_OPEN", "expected": "SOFT_OPEN", "confidence": 70},
        {"actual": "CONTESTABLE", "expected": "CONTESTABLE", "confidence": 80},
    ]
    
    metrics = ClassificationMetrics(results)
    
    print(f"Accuracy: {metrics.accuracy()*100:.1f}%")
    print(f"Macro-avg F1: {metrics.macro_avg_f1():.3f}")
    print(f"Weighted-avg F1: {metrics.weighted_avg_f1():.3f}")
    
    print("\nPer-class metrics:")
    for cls, m in metrics.precision_recall_f1().items():
        print(f"  {cls}: P={m['precision']:.3f}, R={m['recall']:.3f}, F1={m['f1']:.3f}")


def example_6_custom_configuration():
    """Example 6: Custom configuration"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Custom Configuration")
    print("="*60 + "\n")
    
    # Classifier with custom settings
    classifier = ScopeSignalClassifier(
        max_retries=5,
        enable_cache=True,
        cache_dir="/tmp/custom_cache"
    )
    
    result = classifier.classify_update(
        "RFP for electrical upgrades",
        "Electrical"
    )
    
    print(f"Classification: {result['classification']}")
    print(f"Model: {result['_metadata']['model']}")
    print(f"Latency: {result['_metadata']['latency_ms']}ms")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("SCOPESIGNAL USAGE EXAMPLES")
    print("="*60)
    
    try:
        example_1_single_classification()
        example_2_batch_processing()
        example_3_export_results()
        example_4_cache_management()
        example_5_enhanced_metrics()
        example_6_custom_configuration()
        
        print("\n" + "="*60)
        print("ALL EXAMPLES COMPLETED")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        print("\nNote: Some examples require DEEPSEEK_API_KEY to be set.")
