# Quickstart Guide

**Get the system running in under 10 minutes.**

---

## Prerequisites

- Python 3.8+
- LLM API key (currently configured for Anthropic Claude - swappable)

---

## Installation

```bash
# 1. Clone or download this repo
git clone https://github.com/yourusername/scopesignal.git
cd scopesignal

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API key
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=your_key_here

# 5. Verify setup
export ANTHROPIC_API_KEY=your_key_here  # or add to .env and run: source .env
python setup.py
```

If setup.py succeeds, you're ready.

---

## Run Your First Classification

```bash
python -c "
from classifier import classify_update

result = classify_update(
    'RFP issued for electrical upgrades. Bids due March 30.',
    'Electrical'
)

print(f\"Classification: {result['classification']}\")
print(f\"Confidence: {result['confidence']}\")
print(f\"Reasoning: {result['reasoning']}\")
"
```

---

## Run Evaluation Pipeline

### Quick Test (10 samples, verbose output)
```bash
python -m evaluation.evaluate --quick
```

This will:
- Generate 10 simulated updates
- Classify each one
- Show reasoning in real-time
- Report accuracy

**Time:** ~1-2 minutes  
**Cost:** ~$0.05 in API credits

### Full Evaluation (50 samples + adversarial cases)
```bash
python -m evaluation.evaluate
```

This will:
- Generate 50 simulated updates + 5 adversarial edge cases
- Classify each one
- Compare to expected results
- Analyze mismatches
- Save results to `evaluation/results.json`

**Time:** ~5-8 minutes  
**Cost:** ~$0.25 in API credits

---

## Test with Your Own Data

```python
from classifier import BidSignalClassifier

classifier = BidSignalClassifier()

# Paste real agency text here
update = """
Supplemental HVAC work under review; alternates may be considered.
Funding approval pending. Coordination with existing contractor ongoing.
"""

result = classifier.classify_update(update, "HVAC")

print(f"Classification: {result['classification']}")
print(f"Confidence: {result['confidence']}")
print(f"Reasoning: {result['reasoning']}")
print(f"Risk Note: {result['risk_note']}")
print(f"Action: {result['recommended_action']}")
```

---

## Generate Test Data

```python
from data import generate_batch, generate_adversarial_set

# Generate 20 realistic updates
batch = generate_batch(count=20, seed=42)

for update in batch[:5]:
    print(f"{update['id']}: {update['text']}")
    print(f"  Category: {update['category']}")
    print(f"  Expected: {update['expected_classification']}")
    print()

# Generate hard edge cases
adversarial = generate_adversarial_set()
for case in adversarial:
    print(f"{case['id']}: {case['text']}")
    print(f"  Note: {case['note']}")
    print()
```

---

## What to Do Next

### For Portfolio/Interview Prep:
1. ✓ Run full evaluation
2. ✓ Review `evaluation/results.json`
3. ✓ Read mismatch analysis
4. ✓ Push to GitHub
5. ✓ Add screenshot of evaluation results to README

### For Real-World Use:
1. ✓ Scrape 50 real notices from NYC SCA or DDC
2. ✓ Manually classify each
3. ✓ Run through system
4. ✓ Document findings in `evaluation/VALIDATION.md`
5. ✓ Adjust prompt if needed (document why)

### For Expansion (optional):
1. Build simple scraper for one agency portal
2. Add trade-specific rule overlays
3. Create Streamlit dashboard for batch analysis
4. Compare system predictions to actual bid outcomes

---

## Troubleshooting

**Error: "ANTHROPIC_API_KEY not set"**
```bash
export ANTHROPIC_API_KEY=your_key_here
# Or add to .env and run: source .env
```

**Error: "anthropic module not found"**
```bash
pip install -r requirements.txt
```

**Classifications seem too optimistic**
- Expected. Review evaluation results.
- Check if confidence scores are appropriately low on ambiguous cases.
- If consistently over-optimistic, that's a prompt issue (document in VALIDATION.md).

**Rate limiting / API errors**
- System has built-in retry with exponential backoff.
- If persistent, reduce batch size or add longer delays.

---

## Cost Estimate

- Single classification: ~$0.005
- Quick evaluation (10 samples): ~$0.05
- Full evaluation (55 samples): ~$0.25
- Daily monitoring (100 updates): ~$0.50

Based on Claude Sonnet pricing as of 2024.

---

## Getting Help

1. Check existing evaluation results
2. Review VALIDATION_TEMPLATE.md for testing methodology
3. Open GitHub issue with:
   - Exact error message
   - Input text
   - Expected vs actual classification
   - API response (if available)

---

**You're ready. Run `python setup.py` now.**
