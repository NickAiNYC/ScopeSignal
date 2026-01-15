# ScopeSignal Quick Start Guide

Get up and running with ScopeSignal in 5 minutes.

## Installation

```bash
# Clone the repository
git clone https://github.com/NickAiNYC/ScopeSignal.git
cd ScopeSignal

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Get API Key

1. Sign up at https://platform.deepseek.com/
2. Go to https://platform.deepseek.com/api_keys
3. Create a new API key
4. Copy the key

## Configure

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your key
echo "DEEPSEEK_API_KEY=your_key_here" > .env
```

## Verify Installation

```bash
python setup.py
```

You should see:
```
✓ Python 3.x.x
✓ openai x.x.x
✓ API key configured
✓ Test passed - system correctly identified administrative noise
```

## Basic Usage

### 1. Classify Single Update (Python)

```python
from classifier import classify_update

result = classify_update(
    update_text="RFP issued for electrical work. Bids due March 15.",
    trade="Electrical"
)

print(f"Classification: {result['classification']}")
print(f"Confidence: {result['confidence']}%")
print(f"Reasoning: {result['reasoning']}")
```

### 2. Classify Single Update (CLI)

```bash
python -m cli classify "RFP issued for electrical work" --trade Electrical
```

### 3. Batch Processing

```bash
# Process the sample file
python -m cli batch examples/sample_batch.json --output results.csv --summary

# View results
cat results.csv
cat results.txt  # Summary report
```

### 4. Run Evaluation

```bash
# Quick test (10 samples)
python -m evaluation.evaluate --quick

# Full evaluation (50 samples + adversarial)
python -m evaluation.evaluate
```

### 5. Try the Dashboard (Optional)

```bash
# Install dashboard dependencies
pip install streamlit pandas

# Launch dashboard
streamlit run dashboard.py
```

Opens in browser at http://localhost:8501

## Common Tasks

### Check Cache Statistics

```bash
python -m cli cache stats
```

### Clear Cache

```bash
python -m cli cache clear
```

### Export Results to CSV

```python
from classifier import ScopeSignalClassifier, export_to_csv

classifier = ScopeSignalClassifier()
updates = [
    {"text": "Amendment issued", "trade": "Electrical"},
    {"text": "RFP posted", "trade": "HVAC"}
]

results = classifier.classify_batch(updates)
export_to_csv(results, "my_results.csv", include_metadata=True)
```

## Understanding Results

### Classification Types

- **CLOSED** - No opportunity for new subcontractors
  - Administrative noise
  - Incumbent-only work
  - Already awarded
  
- **SOFT_OPEN** - Possible but uncertain opportunity
  - Ambiguous language
  - Insider advantage likely
  - Missing critical details
  
- **CONTESTABLE** - Clear, openly bid-able work
  - Explicit RFP or solicitation
  - Clear scope and deadline
  - Open competition indicated

### Confidence Scores

- **85-100** - Very high confidence (rare)
- **70-84** - High confidence
- **50-69** - Moderate confidence
- **0-49** - Low confidence

The system is **intentionally conservative** - when uncertain, it downgrades classification.

## Next Steps

1. **Read the full README** - Understand the philosophy and limitations
2. **Try the examples** - Run `python examples/usage_examples.py`
3. **Test with real data** - Use your own construction updates
4. **Review metrics** - Check accuracy on the evaluation pipeline
5. **Customize if needed** - Adjust prompt or thresholds (carefully!)

## Troubleshooting

### "DEEPSEEK_API_KEY not set"

Make sure `.env` file exists with your API key:
```bash
cat .env
# Should show: DEEPSEEK_API_KEY=your_key_here
```

### "No module named 'openai'"

Install dependencies:
```bash
pip install -r requirements.txt
```

### Cache not working

Check cache directory permissions:
```bash
ls -la .scopesignal_cache/
```

### Dashboard won't start

Install optional dependencies:
```bash
pip install streamlit pandas
```

## Getting Help

- **Documentation**: See README.md
- **Examples**: See examples/ directory
- **Issues**: Open an issue on GitHub
- **Changelog**: See CHANGELOG.md for version history

## Cost Considerations

- DeepSeek API costs ~$0.001 per classification
- Cache reduces costs by 30-50% for repeated queries
- Batch processing is more efficient than individual calls
- Check usage at https://platform.deepseek.com/usage

## Important Reminders

1. **This is a classification tool, not a guarantee** - Always verify opportunities independently
2. **False negatives are preferred over false positives** - Conservative by design
3. **Cache is local only** - Not shared across machines
4. **Results reflect LLM judgment** - May not match human expert in all cases

---

**Ready to start classifying construction updates!** 🏗️
