"""
Evaluation Pipeline
Tests classifier against simulated and adversarial data.
Produces metrics that prove system quality.
"""

import json
import time
from typing import List, Dict
from pathlib import Path

from classifier import ScopeSignalClassifier, ClassificationError
from data import generate_batch, generate_adversarial_set


class EvaluationResults:
    """Container for evaluation metrics"""
    
    def __init__(self):
        self.total = 0
        self.successful = 0
        self.failed = 0
        self.classifications = {"CLOSED": 0, "SOFT_OPEN": 0, "CONTESTABLE": 0}
        self.matches = 0
        self.mismatches = 0
        self.avg_confidence = 0.0
        self.results_by_category = {}
        self.all_results = []
    
    def add_result(self, update: Dict, classification_result: Dict = None, error: str = None):
        """Add a single classification result"""
        self.total += 1
        
        if error:
            self.failed += 1
            result_entry = {
                "id": update.get("id", "unknown"),
                "text": update["text"],
                "trade": update.get("trade", "unknown"),
                "expected": update.get("expected_classification", "N/A"),
                "actual": "ERROR",
                "confidence": 0,
                "error": error
            }
        else:
            self.successful += 1
            actual = classification_result["classification"]
            expected = update.get("expected_classification", "N/A")
            
            self.classifications[actual] = self.classifications.get(actual, 0) + 1
            
            if expected != "N/A":
                if actual == expected:
                    self.matches += 1
                else:
                    self.mismatches += 1
            
            result_entry = {
                "id": update.get("id", "unknown"),
                "text": update["text"],
                "trade": update.get("trade", "unknown"),
                "expected": expected,
                "actual": actual,
                "confidence": classification_result["confidence"],
                "reasoning": classification_result["reasoning"],
                "risk_note": classification_result["risk_note"],
                "match": actual == expected if expected != "N/A" else None
            }
        
        self.all_results.append(result_entry)
        
        # Track by category if available
        category = update.get("category")
        if category:
            if category not in self.results_by_category:
                self.results_by_category[category] = {"correct": 0, "incorrect": 0, "total": 0}
            
            self.results_by_category[category]["total"] += 1
            
            if result_entry.get("match") is True:
                self.results_by_category[category]["correct"] += 1
            elif result_entry.get("match") is False:
                self.results_by_category[category]["incorrect"] += 1
    
    def compute_metrics(self) -> Dict:
        """Compute summary metrics"""
        confidences = [r["confidence"] for r in self.all_results if r.get("confidence")]
        self.avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        accuracy = self.matches / (self.matches + self.mismatches) if (self.matches + self.mismatches) > 0 else 0
        
        return {
            "total_processed": self.total,
            "successful": self.successful,
            "failed": self.failed,
            "accuracy": round(accuracy * 100, 1),
            "classification_distribution": {
                k: f"{v}/{self.successful} ({round(v/self.successful*100, 1)}%)" 
                for k, v in self.classifications.items()
            },
            "avg_confidence": round(self.avg_confidence, 1),
            "matches": self.matches,
            "mismatches": self.mismatches,
            "results_by_category": {
                cat: {
                    "total": data["total"],
                    "accuracy": f"{round(data['correct']/data['total']*100, 1)}%" if data['total'] > 0 else "N/A"
                }
                for cat, data in self.results_by_category.items()
            }
        }
    
    def print_summary(self):
        """Print human-readable summary"""
        metrics = self.compute_metrics()
        
        print("\n" + "="*60)
        print("EVALUATION SUMMARY")
        print("="*60)
        print(f"\nTotal Updates: {metrics['total_processed']}")
        print(f"Successful: {metrics['successful']}")
        print(f"Failed: {metrics['failed']}")
        print(f"\nAccuracy: {metrics['accuracy']}%")
        print(f"Average Confidence: {metrics['avg_confidence']}")
        
        print("\nClassification Distribution:")
        for classification, count in metrics['classification_distribution'].items():
            print(f"  {classification}: {count}")
        
        print("\nAccuracy by Category:")
        for category, data in metrics['results_by_category'].items():
            print(f"  {category}: {data['accuracy']} ({data['total']} samples)")
        
        print("\n" + "="*60)
    
    def save_results(self, output_path: str):
        """Save detailed results to JSON"""
        output = {
            "summary": self.compute_metrics(),
            "detailed_results": self.all_results
        }
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\nResults saved to: {output_path}")


def run_evaluation(
    sample_size: int = 50,
    include_adversarial: bool = True,
    save_path: str = None,
    verbose: bool = False
) -> EvaluationResults:
    """
    Run full evaluation pipeline.
    
    Args:
        sample_size: Number of simulated updates to test
        include_adversarial: Whether to include adversarial test cases
        save_path: Path to save results JSON (optional)
        verbose: Print individual results as they run
    
    Returns:
        EvaluationResults object
    """
    print(f"\n{'='*60}")
    print("STARTING EVALUATION")
    print(f"{'='*60}\n")
    
    classifier = ScopeSignalClassifier()
    results = EvaluationResults()
    
    # Generate test data
    print(f"Generating {sample_size} simulated updates...")
    batch = generate_batch(count=sample_size, seed=42)
    
    if include_adversarial:
        adversarial = generate_adversarial_set()
        print(f"Adding {len(adversarial)} adversarial cases...")
        batch.extend(adversarial)
    
    print(f"Total test cases: {len(batch)}\n")
    
    # Run classification
    start_time = time.time()
    
    for i, update in enumerate(batch, 1):
        if verbose:
            print(f"\n[{i}/{len(batch)}] Processing: {update['id']}")
            print(f"Text: {update['text']}")
        
        # Map trade to proper case
        trade_map = {"electrical": "Electrical", "hvac": "HVAC", "plumbing": "Plumbing"}
        trade = trade_map.get(update["trade"].lower(), "Electrical")
        
        try:
            classification = classifier.classify_update(update["text"], trade)
            results.add_result(update, classification)
            
            if verbose:
                match_symbol = "✓" if classification["classification"] == update.get("expected_classification") else "✗"
                print(f"{match_symbol} Result: {classification['classification']} (confidence: {classification['confidence']})")
                print(f"  Expected: {update.get('expected_classification', 'N/A')}")
                print(f"  Reasoning: {classification['reasoning']}")
        
        except ClassificationError as e:
            results.add_result(update, error=str(e))
            if verbose:
                print(f"✗ Error: {e}")
        
        # Rate limiting courtesy
        time.sleep(0.5)
    
    elapsed = time.time() - start_time
    print(f"\nCompleted in {elapsed:.1f}s ({elapsed/len(batch):.2f}s per update)")
    
    # Print summary
    results.print_summary()
    
    # Save if requested
    if save_path:
        results.save_results(save_path)
    
    return results


def analyze_mismatches(results: EvaluationResults) -> List[Dict]:
    """
    Extract and analyze cases where classifier disagreed with expected result.
    This is critical for understanding failure modes.
    """
    mismatches = [r for r in results.all_results if r.get("match") is False]
    
    if not mismatches:
        print("\nNo mismatches found!")
        return []
    
    print(f"\n{'='*60}")
    print(f"ANALYZING {len(mismatches)} MISMATCHES")
    print(f"{'='*60}\n")
    
    for i, case in enumerate(mismatches, 1):
        print(f"[{i}] {case['id']}")
        print(f"Text: {case['text']}")
        print(f"Expected: {case['expected']} | Got: {case['actual']} (confidence: {case['confidence']})")
        print(f"Reasoning: {case['reasoning']}")
        print(f"Risk: {case['risk_note']}")
        print()
    
    return mismatches


if __name__ == "__main__":
    import sys
    
    # Quick run vs full evaluation
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        print("Running quick evaluation (10 samples)...\n")
        results = run_evaluation(
            sample_size=10,
            include_adversarial=False,
            verbose=True
        )
    else:
        print("Running full evaluation (50 samples + adversarial)...\n")
        results = run_evaluation(
            sample_size=50,
            include_adversarial=True,
            save_path="evaluation/results.json",
            verbose=False
        )
        
        # Analyze failures
        analyze_mismatches(results)
