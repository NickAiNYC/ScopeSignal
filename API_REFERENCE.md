# API Reference

Complete API documentation for ScopeSignal v2.0.

## Table of Contents

- [Classifier Module](#classifier-module)
- [Cache Module](#cache-module)
- [Export Module](#export-module)
- [Evaluation Module](#evaluation-module)
- [Data Module](#data-module)

---

## Classifier Module

### `classify_update()`

Convenience function for one-off classifications.

**Signature:**
```python
def classify_update(
    update_text: str,
    trade: Literal["Electrical", "HVAC", "Plumbing"],
    api_key: str = None
) -> Dict
```

**Parameters:**
- `update_text` (str): Raw text from agency notice/bulletin/change order
- `trade` (str): One of "Electrical", "HVAC", or "Plumbing"
- `api_key` (str, optional): DeepSeek API key. If None, uses `DEEPSEEK_API_KEY` env var

**Returns:**
- `Dict` with keys:
  - `classification` (str): "CLOSED", "SOFT_OPEN", or "CONTESTABLE"
  - `confidence` (int): 0-100
  - `reasoning` (str): One-sentence explanation
  - `risk_note` (str): What could make this wrong
  - `recommended_action` (str): Next step for subcontractor
  - `trade_relevant` (bool): Whether update is relevant to specified trade
  - `_metadata` (Dict): Model info, latency, cache status

**Example:**
```python
from classifier import classify_update

result = classify_update(
    update_text="RFP issued for electrical work. Bids due March 15.",
    trade="Electrical"
)

print(result["classification"])  # "CONTESTABLE"
print(result["confidence"])      # 85
```

---

### `ScopeSignalClassifier`

Main classifier class with caching and batch processing.

**Signature:**
```python
class ScopeSignalClassifier:
    def __init__(
        self,
        api_key: str = None,
        max_retries: int = 3,
        enable_cache: bool = True,
        cache_dir: str = ".scopesignal_cache"
    )
```

**Parameters:**
- `api_key` (str, optional): DeepSeek API key
- `max_retries` (int): Number of retry attempts for failed API calls
- `enable_cache` (bool): Whether to enable caching
- `cache_dir` (str): Directory for cache files

**Methods:**

#### `classify_update()`
Same as standalone function but uses instance configuration.

#### `classify_batch()`
Process multiple updates efficiently.

**Signature:**
```python
def classify_batch(
    self,
    updates: List[Dict[str, str]],
    show_progress: bool = True
) -> List[Dict]
```

**Parameters:**
- `updates` (List[Dict]): List of dicts with `text` and `trade` keys
- `show_progress` (bool): Whether to print progress updates

**Returns:**
- `List[Dict]`: List of classification results

**Example:**
```python
from classifier import ScopeSignalClassifier

classifier = ScopeSignalClassifier()

updates = [
    {"text": "Amendment 2 issued", "trade": "Electrical"},
    {"text": "RFP posted", "trade": "HVAC"}
]

results = classifier.classify_batch(updates)
```

---

## Cache Module

### `ResultCache`

File-based cache for classification results.

**Signature:**
```python
class ResultCache:
    def __init__(
        self,
        cache_dir: str = ".scopesignal_cache",
        ttl_seconds: int = 86400
    )
```

**Parameters:**
- `cache_dir` (str): Directory to store cache files
- `ttl_seconds` (int): Time-to-live for cache entries (default: 24 hours)

**Methods:**

#### `get(cache_key: str) -> Optional[Dict]`
Retrieve cached result if it exists and is not expired.

#### `set(cache_key: str, result: Dict) -> None`
Store result in cache.

#### `clear() -> int`
Clear all cached results. Returns number of entries removed.

#### `stats() -> Dict`
Get cache statistics (entries, size, age).

**Example:**
```python
from classifier.cache import ResultCache

cache = ResultCache()
stats = cache.stats()
print(f"Cache entries: {stats['entries']}")

# Clear cache
cleared = cache.clear()
print(f"Cleared {cleared} entries")
```

---

## Export Module

### `export_to_csv()`

Export classification results to CSV format.

**Signature:**
```python
def export_to_csv(
    results: List[Dict],
    output_path: str,
    include_metadata: bool = False
) -> None
```

**Parameters:**
- `results` (List[Dict]): Classification results
- `output_path` (str): Path to output CSV file
- `include_metadata` (bool): Whether to include metadata columns

**Example:**
```python
from classifier import export_to_csv

export_to_csv(results, "results.csv", include_metadata=True)
```

---

### `export_to_json()`

Export classification results to JSON format.

**Signature:**
```python
def export_to_json(
    results: List[Dict],
    output_path: str,
    pretty: bool = True,
    include_metadata: bool = True
) -> None
```

**Parameters:**
- `results` (List[Dict]): Classification results
- `output_path` (str): Path to output JSON file
- `pretty` (bool): Whether to format with indentation
- `include_metadata` (bool): Whether to include metadata fields

---

### `export_summary_report()`

Export a summary report of classification results.

**Signature:**
```python
def export_summary_report(
    results: List[Dict],
    output_path: str
) -> None
```

**Parameters:**
- `results` (List[Dict]): Classification results
- `output_path` (str): Path to output text file

**Output includes:**
- Total updates processed
- Classification distribution
- Average confidence
- List of contestable opportunities

---

## Evaluation Module

### `ClassificationMetrics`

Calculate detailed performance metrics.

**Signature:**
```python
class ClassificationMetrics:
    def __init__(self, results: List[Dict])
```

**Parameters:**
- `results` (List[Dict]): Classification results with `actual` and `expected` fields

**Methods:**

#### `confusion_matrix() -> Dict[str, Dict[str, int]]`
Calculate confusion matrix.

#### `precision_recall_f1() -> Dict[str, Dict[str, float]]`
Calculate precision, recall, and F1 score for each class.

#### `macro_avg_f1() -> float`
Calculate macro-averaged F1 score.

#### `weighted_avg_f1() -> float`
Calculate weighted-average F1 score.

#### `accuracy() -> float`
Calculate overall accuracy.

#### `confidence_analysis() -> Dict[str, float]`
Analyze confidence scores by classification.

#### `print_report() -> None`
Print comprehensive metrics report.

**Example:**
```python
from evaluation import ClassificationMetrics

metrics = ClassificationMetrics(results)
metrics.print_report()

print(f"Accuracy: {metrics.accuracy()*100:.1f}%")
print(f"F1 Score: {metrics.macro_avg_f1():.3f}")
```

---

### `run_evaluation()`

Run full evaluation pipeline.

**Signature:**
```python
def run_evaluation(
    sample_size: int = 50,
    include_adversarial: bool = True,
    save_path: str = None,
    verbose: bool = False
) -> EvaluationResults
```

**Parameters:**
- `sample_size` (int): Number of simulated updates to test
- `include_adversarial` (bool): Whether to include adversarial test cases
- `save_path` (str, optional): Path to save results JSON
- `verbose` (bool): Print individual results as they run

**Returns:**
- `EvaluationResults` object with metrics and detailed results

---

## Data Module

### `generate_update()`

Generate a single realistic project update.

**Signature:**
```python
def generate_update(
    category: str = None,
    trade: Literal["electrical", "HVAC", "plumbing"] = None,
    seed: int = None
) -> Dict
```

**Parameters:**
- `category` (str, optional): Specific category or None for random
- `trade` (str, optional): Specific trade or None for random
- `seed` (int, optional): Random seed for reproducibility

**Returns:**
- `Dict` with `text`, `category`, `trade`, `expected_classification` keys

---

### `generate_batch()`

Generate a batch of realistic updates.

**Signature:**
```python
def generate_batch(
    count: int = 100,
    category_distribution: Dict[str, float] = None,
    seed: int = None
) -> List[Dict]
```

**Parameters:**
- `count` (int): Number of updates to generate
- `category_distribution` (Dict, optional): Custom distribution
- `seed` (int, optional): Random seed

**Returns:**
- `List[Dict]` of updates

---

## Error Handling

### `ClassificationError`

Raised when classification fails after retries.

**Example:**
```python
from classifier import ClassificationError

try:
    result = classify_update("Update text", "Electrical")
except ClassificationError as e:
    print(f"Classification failed: {e}")
```

---

## Type Hints

All functions use type hints for better IDE support and type checking:

```python
from typing import Dict, List, Literal, Optional

# Example function signatures
def classify_update(
    update_text: str,
    trade: Literal["Electrical", "HVAC", "Plumbing"],
    api_key: Optional[str] = None
) -> Dict:
    ...
```

---

## Configuration

### Environment Variables

- `DEEPSEEK_API_KEY`: API key for DeepSeek (required)

### Constants

Default values can be customized:

```python
# Cache TTL (seconds)
cache = ResultCache(ttl_seconds=3600)  # 1 hour

# Retry attempts
classifier = ScopeSignalClassifier(max_retries=5)

# Disable cache
classifier = ScopeSignalClassifier(enable_cache=False)
```

---

## Best Practices

1. **Reuse classifier instances** for better cache utilization
2. **Use batch processing** for multiple updates
3. **Monitor cache hit rates** to optimize performance
4. **Handle ClassificationError** appropriately
5. **Export results** for manual review and analysis

---

For more examples, see the [examples/](examples/) directory.
