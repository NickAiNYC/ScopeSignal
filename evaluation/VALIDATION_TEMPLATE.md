# Validation Notes

**This document records manual review of real agency data.**

The purpose is to identify failure modes, not celebrate accuracy.

---

## Validation Methodology

1. Scraped 50 real notices from [source]
2. Manually classified each based on contractor judgment
3. Ran through classifier
4. Compared results
5. Analyzed disagreements

---

## Results Summary

**Date:** [YYYY-MM-DD]  
**Source:** [NYC SCA / DDC / HPD]  
**Sample Size:** [N]  
**Trades Tested:** [Electrical / HVAC / Plumbing]

### Classification Distribution

| Category | Count | Percentage |
|----------|-------|------------|
| CLOSED | X | XX% |
| SOFT_OPEN | X | XX% |
| CONTESTABLE | X | XX% |

### Agreement with Manual Classification

- **Exact match:** X/N (XX%)
- **One level off:** X/N (XX%)
- **Two levels off:** X/N (XX%)

---

## Notable Cases

### Case 1: [Brief description]

**Text:** "..."

**Expected:** CLOSED  
**Got:** SOFT_OPEN  
**Confidence:** 65

**Analysis:**  
Classifier detected [keyword] and interpreted it as potential opportunity. Manual review reveals this is [incumbent work / administrative / other]. 

**Pattern:** System may be over-weighting [specific language pattern].

---

### Case 2: [Brief description]

**Text:** "..."

**Expected:** CONTESTABLE  
**Got:** CLOSED  
**Confidence:** 80

**Analysis:**  
Classifier dismissed this due to [missing context / ambiguous language]. However, follow-up research shows this was legitimately open for bidding.

**Pattern:** System may be too conservative on [specific scenario].

---

## Observed Failure Modes

1. **[Pattern 1]:** Description of recurring classification error
   - Frequency: X instances
   - Impact: False negative / false positive
   - Possible fix: Adjust prompt / add rule / accept limitation

2. **[Pattern 2]:** ...

---

## Contractor Feedback

**Source:** [Name/role], [Company], [Date]

**Key insights:**
- [Quote or paraphrased feedback]
- [Specific correction to system logic]

---

## Recommended Adjustments

Based on validation findings:

1. **[Adjustment 1]:** Reason and expected impact
2. **[Adjustment 2]:** ...

**Not recommended:**
- [Adjustment that would add complexity without clear benefit]
- [Adjustment that would reduce conservative bias]

---

## Next Validation

- [ ] Test on [different agency]
- [ ] Test on [different trade]
- [ ] Re-test after prompt adjustments
- [ ] Compare against contractor predictions (blind test)

---

## Notes

- Validation is never complete - agency language constantly evolves
- One contractor's "obvious closed" is another's "worth checking"
- System should reflect majority contractor judgment, not edge cases
- When in doubt, maintain conservative bias
