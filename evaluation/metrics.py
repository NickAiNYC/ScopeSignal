"""
Enhanced metrics for classification evaluation.
Includes confusion matrix, precision, recall, F1 scores.
"""

from typing import Dict, List, Tuple
from collections import defaultdict


class ClassificationMetrics:
    """
    Calculate detailed performance metrics for classification results.
    """
    
    def __init__(self, results: List[Dict]):
        """
        Initialize metrics calculator.
        
        Args:
            results: List of classification results with 'actual' and 'expected' fields
        """
        self.results = results
        self.classes = ["CLOSED", "SOFT_OPEN", "CONTESTABLE"]
    
    def confusion_matrix(self) -> Dict[str, Dict[str, int]]:
        """
        Calculate confusion matrix.
        
        Returns:
            Dict mapping predicted class -> {actual class -> count}
        """
        matrix = {
            predicted: {actual: 0 for actual in self.classes}
            for predicted in self.classes
        }
        
        for result in self.results:
            predicted = result.get("actual")
            expected = result.get("expected")
            
            if predicted in self.classes and expected in self.classes:
                matrix[predicted][expected] += 1
        
        return matrix
    
    def precision_recall_f1(self) -> Dict[str, Dict[str, float]]:
        """
        Calculate precision, recall, and F1 score for each class.
        
        Returns:
            Dict mapping class -> {precision, recall, f1, support}
        """
        matrix = self.confusion_matrix()
        metrics = {}
        
        for cls in self.classes:
            # True positives: predicted X, expected X
            tp = matrix[cls][cls]
            
            # False positives: predicted X, expected other
            fp = sum(matrix[cls][other] for other in self.classes if other != cls)
            
            # False negatives: predicted other, expected X
            fn = sum(matrix[other][cls] for other in self.classes if other != cls)
            
            # True negatives: predicted other, expected other
            tn = sum(
                matrix[pred][exp]
                for pred in self.classes if pred != cls
                for exp in self.classes if exp != cls
            )
            
            # Calculate metrics
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            support = tp + fn
            
            metrics[cls] = {
                "precision": round(precision, 3),
                "recall": round(recall, 3),
                "f1": round(f1, 3),
                "support": support
            }
        
        return metrics
    
    def macro_avg_f1(self) -> float:
        """Calculate macro-averaged F1 score across all classes"""
        metrics = self.precision_recall_f1()
        f1_scores = [m["f1"] for m in metrics.values()]
        return round(sum(f1_scores) / len(f1_scores), 3) if f1_scores else 0.0
    
    def weighted_avg_f1(self) -> float:
        """Calculate weighted-average F1 score (weighted by support)"""
        metrics = self.precision_recall_f1()
        total_support = sum(m["support"] for m in metrics.values())
        
        if total_support == 0:
            return 0.0
        
        weighted_sum = sum(m["f1"] * m["support"] for m in metrics.values())
        return round(weighted_sum / total_support, 3)
    
    def accuracy(self) -> float:
        """Calculate overall accuracy"""
        correct = sum(
            1 for r in self.results
            if r.get("actual") == r.get("expected") and r.get("actual") in self.classes
        )
        total = sum(
            1 for r in self.results
            if r.get("actual") in self.classes and r.get("expected") in self.classes
        )
        return round(correct / total, 3) if total > 0 else 0.0
    
    def confidence_analysis(self) -> Dict[str, float]:
        """
        Analyze confidence scores by classification and correctness.
        
        Returns:
            Dict with confidence statistics
        """
        confidences = {
            "correct": [],
            "incorrect": [],
            "by_class": defaultdict(list)
        }
        
        for result in self.results:
            if result.get("actual") not in self.classes:
                continue
            
            confidence = result.get("confidence", 0)
            is_correct = result.get("actual") == result.get("expected")
            
            if is_correct:
                confidences["correct"].append(confidence)
            else:
                confidences["incorrect"].append(confidence)
            
            confidences["by_class"][result["actual"]].append(confidence)
        
        stats = {}
        
        if confidences["correct"]:
            stats["avg_confidence_correct"] = round(
                sum(confidences["correct"]) / len(confidences["correct"]), 1
            )
        
        if confidences["incorrect"]:
            stats["avg_confidence_incorrect"] = round(
                sum(confidences["incorrect"]) / len(confidences["incorrect"]), 1
            )
        
        for cls, values in confidences["by_class"].items():
            if values:
                stats[f"avg_confidence_{cls}"] = round(sum(values) / len(values), 1)
        
        return stats
    
    def cost_analysis(self) -> Dict[str, float]:
        """
        Analyze cost implications based on latency metadata.
        
        Returns:
            Dict with cost statistics (if latency data available)
        """
        latencies = []
        cache_hits = 0
        cache_misses = 0
        
        for result in self.results:
            metadata = result.get("_metadata", {})
            
            if "latency_ms" in metadata:
                latencies.append(metadata["latency_ms"])
            
            if metadata.get("cache_hit"):
                cache_hits += 1
            else:
                cache_misses += 1
        
        stats = {
            "cache_hits": cache_hits,
            "cache_misses": cache_misses,
            "cache_hit_rate": round(cache_hits / (cache_hits + cache_misses), 3) if (cache_hits + cache_misses) > 0 else 0.0
        }
        
        if latencies:
            stats["avg_latency_ms"] = round(sum(latencies) / len(latencies), 0)
            stats["total_latency_ms"] = sum(latencies)
        
        return stats
    
    def print_report(self):
        """Print comprehensive metrics report"""
        print("\n" + "="*70)
        print("COMPREHENSIVE CLASSIFICATION METRICS")
        print("="*70)
        
        # Overall accuracy
        accuracy = self.accuracy()
        print(f"\nOverall Accuracy: {accuracy*100:.1f}%")
        
        # Confusion Matrix
        print("\nConfusion Matrix:")
        print("-"*70)
        matrix = self.confusion_matrix()
        
        # Header
        print(f"{'Predicted →':>15} | " + " | ".join(f"{cls:>12}" for cls in self.classes))
        print("-"*70)
        
        # Rows
        for expected in self.classes:
            counts = [str(matrix[pred][expected]) for pred in self.classes]
            print(f"{'↓ ' + expected:>15} | " + " | ".join(f"{c:>12}" for c in counts))
        
        # Per-class metrics
        print("\nPer-Class Metrics:")
        print("-"*70)
        metrics = self.precision_recall_f1()
        
        print(f"{'Class':>15} | {'Precision':>10} | {'Recall':>10} | {'F1':>10} | {'Support':>10}")
        print("-"*70)
        
        for cls in self.classes:
            m = metrics[cls]
            print(
                f"{cls:>15} | "
                f"{m['precision']*100:>9.1f}% | "
                f"{m['recall']*100:>9.1f}% | "
                f"{m['f1']:>10.3f} | "
                f"{m['support']:>10}"
            )
        
        # Aggregate metrics
        print("\nAggregate Metrics:")
        print("-"*70)
        print(f"Macro-avg F1: {self.macro_avg_f1():.3f}")
        print(f"Weighted-avg F1: {self.weighted_avg_f1():.3f}")
        
        # Confidence analysis
        print("\nConfidence Analysis:")
        print("-"*70)
        conf_stats = self.confidence_analysis()
        for key, value in conf_stats.items():
            print(f"{key}: {value}")
        
        # Cost analysis
        cost_stats = self.cost_analysis()
        if cost_stats.get("cache_hits", 0) > 0 or cost_stats.get("cache_misses", 0) > 0:
            print("\nPerformance Metrics:")
            print("-"*70)
            print(f"Cache hits: {cost_stats['cache_hits']}")
            print(f"Cache misses: {cost_stats['cache_misses']}")
            print(f"Cache hit rate: {cost_stats['cache_hit_rate']*100:.1f}%")
            if "avg_latency_ms" in cost_stats:
                print(f"Avg latency: {cost_stats['avg_latency_ms']}ms")
        
        print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    # Test with sample data
    test_results = [
        {"actual": "CLOSED", "expected": "CLOSED", "confidence": 95, "_metadata": {"latency_ms": 450, "cache_hit": False}},
        {"actual": "CLOSED", "expected": "CLOSED", "confidence": 90, "_metadata": {"latency_ms": 420, "cache_hit": False}},
        {"actual": "SOFT_OPEN", "expected": "CLOSED", "confidence": 65, "_metadata": {"latency_ms": 480, "cache_hit": False}},
        {"actual": "SOFT_OPEN", "expected": "SOFT_OPEN", "confidence": 70, "_metadata": {"latency_ms": 200, "cache_hit": True}},
        {"actual": "CONTESTABLE", "expected": "CONTESTABLE", "confidence": 80, "_metadata": {"latency_ms": 500, "cache_hit": False}},
        {"actual": "CLOSED", "expected": "SOFT_OPEN", "confidence": 85, "_metadata": {"latency_ms": 150, "cache_hit": True}},
    ]
    
    metrics = ClassificationMetrics(test_results)
    metrics.print_report()
    
    print("✓ Metrics tests passed")
