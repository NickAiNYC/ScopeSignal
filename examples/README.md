# ScopeSignal Examples

This directory contains examples demonstrating ScopeSignal's features.

## Files

- **sample_batch.json** - Sample JSON file for batch processing
- **usage_examples.py** - Comprehensive Python examples demonstrating all features

## Quick Start

### Run All Examples

```bash
python examples/usage_examples.py
```

### CLI Examples

```bash
# Classify single update
python -m cli classify "RFP issued for electrical work" --trade Electrical --json

# Batch process
python -m cli batch examples/sample_batch.json --output results.csv --summary

# Cache management
python -m cli cache stats
```

### Python API Examples

```python
from classifier import classify_update, ScopeSignalClassifier

# Single classification
result = classify_update(
    update_text="Amendment 2 issued",
    trade="Electrical"
)

# Batch processing
classifier = ScopeSignalClassifier()
updates = [
    {"text": "RFP posted", "trade": "Electrical"},
    {"text": "Change order issued", "trade": "HVAC"}
]
results = classifier.classify_batch(updates)
```

### Dashboard

```bash
# Install dashboard dependencies
pip install streamlit pandas

# Run dashboard
streamlit run dashboard.py
```

## Input Format for Batch Processing

JSON file with array of updates:

```json
{
  "updates": [
    {
      "id": "update_001",
      "text": "Project update text here",
      "trade": "Electrical"
    }
  ]
}
```

Required fields:
- `text` - The project update text
- `trade` - One of: Electrical, HVAC, Plumbing

Optional fields:
- `id` - Identifier for the update
