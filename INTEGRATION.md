# ConComplyAi Integration

This document describes the integration of ScopeSignal into the ConComplyAi Monorepo.

## Overview

The integration combines ScopeSignal's conservative opportunity classification with ConComplyAi's compliance verification to create a comprehensive "Project Matching Engine" for NYC construction subcontractors.

## Architecture

### Package Structure

```
/packages
├── agents/
│   └── opportunity/          # Conservative Classifier
│       ├── classifier.py     # OpportunityClassifier with audit trail
│       ├── decision_proof.py # Audit trail for classifications
│       └── __init__.py
└── compliance/               # ConComplyAi Integration
    ├── feasibility.py        # Feasibility Score calculator
    ├── insurance.py          # Insurance limits validator
    ├── license.py            # Trade license validator
    └── __init__.py
```

### Components

```
/components/modules
└── VeteranDashboard.tsx     # UI for filtered opportunities + compliance
```

### API Endpoints

```
/app/api
├── feasibility/             # POST - Calculate feasibility score
│   └── route.ts
└── veteran-dashboard/       # GET/POST - Dashboard data with filtering
    └── route.ts
```

## Key Features

### 1. Conservative Classifier with Audit Trail

The `OpportunityClassifier` wraps ScopeSignal's core logic with `DecisionProof` audit trails:

```python
from packages.agents.opportunity import OpportunityClassifier

classifier = OpportunityClassifier()
result, proof = classifier.classify_with_proof(
    update_text="RFP issued for electrical work",
    trade="Electrical",
    agency="SCA"
)

# Access classification
print(result['classification'])  # "CONTESTABLE"

# Access audit trail
print(proof.to_json())  # Full reasoning chain
```

**Key Benefits:**
- Full traceability of classification decisions
- Validation checks recorded
- Skeptical-by-default philosophy maintained
- Compatible with ConComplyAi's compliance audit trails

### 2. Feasibility Score Function

The `FeasibilityScorer` cross-references opportunities with user compliance data:

```python
from packages.compliance import check_feasibility

user_insurance = {
    "general_liability": 2.0,
    "auto_liability": 1.0,
    "umbrella": 5.0,
    "workers_comp": 1.0
}

user_licenses = [{
    "type": "Master Electrician",
    "status": "active",
    "expiry": "2027-12-31"
}]

feasibility = check_feasibility(
    opportunity_classification=result,
    user_insurance=user_insurance,
    user_licenses=user_licenses,
    agency="SCA"
)

print(feasibility['can_bid'])           # True/False
print(feasibility['feasibility_score']) # 0-100
print(feasibility['blockers'])          # List of compliance issues
```

**Scoring Algorithm:**
1. **Base Score**: Derived from opportunity confidence
   - CONTESTABLE: 100% of confidence
   - SOFT_OPEN: 60% of confidence
   - CLOSED: 0

2. **Compliance Multipliers**:
   - Missing insurance: 70% penalty
   - Missing license: 80% penalty

3. **Final Decision**: Can bid only if CONTESTABLE/SOFT_OPEN AND fully compliant

### 3. Agency-Specific Insurance Requirements

Different NYC agencies have different insurance thresholds:

```python
from packages.compliance import InsuranceValidator

validator = InsuranceValidator()

# SCA (School Construction Authority) - Higher limits
sca_requirements = validator.get_agency_requirements("SCA")
# {"general_liability": 2.0M, "umbrella": 5.0M, ...}

# DDC (Department of Design and Construction) - Standard limits
ddc_requirements = validator.get_agency_requirements("DDC")
# {"general_liability": 1.0M, "umbrella": 2.0M, ...}
```

**Supported Agencies:**
- SCA: School Construction Authority (highest requirements)
- DDC: Department of Design and Construction
- HPD: Housing Preservation and Development
- DEP: Department of Environmental Protection
- NYCHA: NYC Housing Authority

### 4. Trade License Validation

Validates active licenses for specific trades:

```python
from packages.compliance import LicenseValidator

validator = LicenseValidator()

result = validator.validate_license(
    user_licenses=user_licenses,
    trade="Electrical"
)

print(result['compliant'])        # True/False
print(result['active_licenses'])  # ["Master Electrician"]
print(result['expired_licenses']) # []
```

**Supported Trades:**
- Electrical: Master Electrician, Electrical Contractor
- Plumbing: Master Plumber, Plumbing Contractor
- HVAC: HVAC License, Mechanical Contractor

### 5. Veteran Dashboard

The Veteran Dashboard provides a filtered view of opportunities with compliance status:

**Features:**
- Filter by Opportunity Level (CLOSED/SOFT_OPEN/CONTESTABLE)
- Filter by Trade (Electrical/HVAC/Plumbing)
- Show only compliant opportunities
- Green check ✓ for compliance readiness
- Real-time feasibility scoring

**Access:** `/veteran-dashboard`

## API Usage

### POST /api/feasibility

Calculate feasibility for a single opportunity:

```typescript
const response = await fetch('/api/feasibility', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    update_text: "RFP issued for electrical work",
    trade: "Electrical",
    agency: "SCA",
    user_insurance: {
      general_liability: 2.0,
      auto_liability: 1.0,
      umbrella: 5.0,
      workers_comp: 1.0
    },
    user_licenses: [{
      type: "Master Electrician",
      status: "active",
      expiry: "2027-12-31"
    }]
  })
})

const { classification, feasibility } = await response.json()
```

### GET /api/veteran-dashboard

Fetch filtered opportunities:

```typescript
const response = await fetch(
  '/api/veteran-dashboard?trade=Electrical&opportunityLevel=CONTESTABLE&complianceReady=true'
)

const { projects, filters } = await response.json()
```

## Testing

### Integration Tests

Run the full integration test suite:

```bash
python -m pytest tests/integration/test_simulator_integration.py -v
```

**Test Coverage:**
- ✅ Simulator generates valid "ugly" agency text
- ✅ Batch generation maintains realistic distribution (CONTESTABLE < 5%)
- ✅ DecisionProof audit trails work correctly
- ✅ Feasibility scoring for compliant/non-compliant users
- ✅ CLOSED opportunities always score 0
- ✅ Batch feasibility calculation

### Running Specific Tests

```bash
# Test simulator integration
pytest tests/integration/test_simulator_integration.py::TestSimulatorIntegration -v

# Test feasibility scoring
pytest tests/integration/test_simulator_integration.py::TestFeasibilityScorerIntegration -v

# Test skewed data handling
pytest tests/integration/test_simulator_integration.py::TestSkewedDataHandling -v
```

## Design Philosophy

### Skeptical by Default

The integration maintains ScopeSignal's core philosophy:

1. **Conservative Classification**: When uncertain, downgrade
2. **Realistic Scoring**: Even CONTESTABLE opportunities are discounted by compliance
3. **Transparency**: Full audit trails for all decisions
4. **Reality Check**: CONTESTABLE is rare (~2%), as in real life

### DecisionProof Alignment

The `DecisionProof` audit trail provides the same level of traceability as ConComplyAi's compliance checks:

- All inputs recorded
- Reasoning chain captured
- Validation checks logged
- Metadata preserved

This allows reviewers to understand exactly why an opportunity was classified and scored as it was.

## Example Workflow

Complete workflow from classification to bidding decision:

```python
from packages.agents.opportunity import OpportunityClassifier
from packages.compliance import check_feasibility

# Step 1: Initialize classifier
classifier = OpportunityClassifier()

# Step 2: Classify opportunity with audit trail
update_text = "RFP issued for HVAC system upgrade. Bids due March 15."
result, proof = classifier.classify_with_proof(
    update_text=update_text,
    trade="HVAC",
    agency="SCA"
)

# Step 3: Define user compliance data
user_insurance = {
    "general_liability": 2.0,
    "auto_liability": 1.0,
    "umbrella": 5.0,
    "workers_comp": 1.0
}

user_licenses = [{
    "type": "HVAC License",
    "status": "active",
    "expiry": "2027-06-30"
}]

# Step 4: Calculate feasibility
feasibility = check_feasibility(
    result,
    user_insurance,
    user_licenses,
    "SCA"
)

# Step 5: Make decision
if feasibility['can_bid']:
    print(f"✓ GO: Feasibility score {feasibility['feasibility_score']}")
    print(f"Classification: {result['classification']}")
    print(f"Confidence: {result['confidence']}%")
else:
    print(f"✗ NO GO: {', '.join(feasibility['blockers'])}")
    print(f"Recommendations: {', '.join(feasibility['recommendations'])}")

# Step 6: Review audit trail (optional)
print("\n=== Audit Trail ===")
print(proof.to_json())
```

## Known Limitations

1. **Mock Data**: Current implementation uses mock project data. In production, this would query a database of actual NYC agency updates.

2. **User Data**: Current implementation uses mock user compliance data. In production, this would fetch from user profiles.

3. **Agency Quirks**: Some agency-specific behaviors (e.g., SCA's preference for incumbents) are not yet modeled.

4. **Attachments**: Cannot analyze referenced attachments or drawings.

5. **Historical Data**: No historical analysis of prediction accuracy yet.

## Future Enhancements

1. **Real-Time Agency Feeds**: Scrape SCA, DDC, HPD portals
2. **Historical Tracking**: Track classification accuracy over time
3. **User Profiles**: Store and manage user insurance/license data
4. **Notification System**: Alert users when compliant opportunities appear
5. **Multi-Provider LLM**: Support Claude, OpenAI, Gemini backends

## Contributing

When extending this integration:

1. **Maintain Skepticism**: Don't optimize for accuracy at the cost of conservatism
2. **Preserve Audit Trails**: All decisions must be traceable
3. **Test with Ugly Data**: Use the simulator to generate realistic test cases
4. **Document Assumptions**: Make implicit knowledge explicit

## License

Same as ScopeSignal: MIT
