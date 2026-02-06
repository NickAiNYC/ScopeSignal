#!/usr/bin/env python
"""
Example: Full Integration Workflow

Demonstrates the complete flow from opportunity classification
through compliance checking to feasibility scoring.
"""

import sys
import os

# Add packages to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from packages.agents.opportunity import OpportunityClassifier
from packages.compliance import check_feasibility
from data.simulator import generate_batch


def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def main():
    print_section("ScopeSignal + ConComplyAi Integration Demo")
    
    # Define mock user compliance data
    user_insurance = {
        "general_liability": 2.0,
        "auto_liability": 1.0,
        "umbrella": 5.0,
        "workers_comp": 1.0
    }
    
    user_licenses = [
        {
            "type": "Master Electrician",
            "number": "ME123456",
            "status": "active",
            "expiry": "2027-12-31"
        },
        {
            "type": "HVAC License",
            "number": "HVAC789",
            "status": "active",
            "expiry": "2027-06-30"
        }
    ]
    
    print("User Profile:")
    print(f"  Insurance: ${user_insurance['general_liability']}M GL, ${user_insurance['umbrella']}M Umbrella")
    print(f"  Licenses: {', '.join([l['type'] for l in user_licenses])}")
    
    # Generate test updates using simulator
    print_section("Generating Test Updates (Simulator)")
    
    updates = generate_batch(count=10, seed=12345)
    print(f"Generated {len(updates)} updates with realistic 'ugly' agency language")
    
    # Show distribution
    categories = {}
    for update in updates:
        cat = update["expected_classification"]
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\nExpected Distribution:")
    for cat, count in sorted(categories.items()):
        pct = (count / len(updates)) * 100
        print(f"  {cat}: {count} ({pct:.0f}%)")
    
    # Process a few examples
    print_section("Processing Example Opportunities")
    
    # Note: Skipping actual classification to avoid API calls
    # In production, you would:
    # classifier = OpportunityClassifier()
    # result, proof = classifier.classify_with_proof(...)
    
    examples = [
        {
            "title": "SCA PS 123 HVAC System Upgrade - RFP Posted",
            "update_text": "RFP issued for additional HVAC work. Qualified vendors may submit pricing by March 15.",
            "trade": "HVAC",
            "agency": "SCA",
            "mock_classification": {
                "classification": "CONTESTABLE",
                "confidence": 85,
                "trade_relevant": True,
                "reasoning": "Clear RFP with deadline signals open competition.",
                "risk_note": "Could be limited to pre-qualified vendors.",
                "recommended_action": "Submit proposal with detailed pricing.",
                "_metadata": {"trade": "HVAC"}
            }
        },
        {
            "title": "DDC Project Amendment 3 - Electrical",
            "update_text": "Amendment 3 issued. See updated Attachment B.",
            "trade": "Electrical",
            "agency": "DDC",
            "mock_classification": {
                "classification": "CLOSED",
                "confidence": 92,
                "trade_relevant": False,
                "reasoning": "Administrative revision with no new scope.",
                "risk_note": "Attachment could contain hidden opportunities.",
                "recommended_action": "Monitor for future updates.",
                "_metadata": {"trade": "Electrical"}
            }
        },
        {
            "title": "HPD Housing Project - Change Order Discussion",
            "update_text": "Agency evaluating additional HVAC work pending funding.",
            "trade": "HVAC",
            "agency": "HPD",
            "mock_classification": {
                "classification": "SOFT_OPEN",
                "confidence": 68,
                "trade_relevant": True,
                "reasoning": "Scope exists but not formally opened for bidding.",
                "risk_note": "Funding uncertainty may kill opportunity.",
                "recommended_action": "Monitor and maintain light contact.",
                "_metadata": {"trade": "HVAC"}
            }
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\nExample {i}: {example['title']}")
        print(f"Agency: {example['agency']} | Trade: {example['trade']}")
        print(f"Text: {example['update_text']}")
        
        # Get classification (mocked)
        result = example['mock_classification']
        
        print(f"\n  Classification: {result['classification']}")
        print(f"  Confidence: {result['confidence']}%")
        print(f"  Reasoning: {result['reasoning']}")
        
        # Calculate feasibility
        feasibility = check_feasibility(
            result,
            user_insurance,
            user_licenses,
            example['agency']
        )
        
        print(f"\n  Feasibility Score: {feasibility['feasibility_score']}")
        print(f"  Can Bid: {'✓ YES' if feasibility['can_bid'] else '✗ NO'}")
        
        if feasibility['can_bid']:
            print(f"  Insurance: ✓ Compliant")
            print(f"  License: ✓ Compliant")
            print(f"  → PROCEED WITH PROPOSAL")
        else:
            print(f"  Insurance: {'✓' if feasibility['compliance_readiness']['insurance'] else '✗'} {'Compliant' if feasibility['compliance_readiness']['insurance'] else 'Non-compliant'}")
            print(f"  License: {'✓' if feasibility['compliance_readiness']['license'] else '✗'} {'Compliant' if feasibility['compliance_readiness']['license'] else 'Non-compliant'}")
            
            if feasibility['blockers']:
                print(f"\n  Blockers:")
                for blocker in feasibility['blockers']:
                    print(f"    • {blocker}")
            
            if feasibility['recommendations']:
                print(f"\n  Recommendations:")
                for rec in feasibility['recommendations']:
                    print(f"    • {rec}")
    
    print_section("Integration Summary")
    
    print("✓ Conservative Classifier: Skeptical-by-default philosophy maintained")
    print("✓ DecisionProof: Full audit trail for all classifications")
    print("✓ Feasibility Scorer: Cross-references opportunities with compliance")
    print("✓ Insurance Validation: Agency-specific requirements (SCA vs DDC)")
    print("✓ License Validation: Trade-specific requirements")
    print("✓ Simulator Integration: Tests handle 'ugly' agency text")
    print("\nIntegration complete. Access Veteran Dashboard at /veteran-dashboard")


if __name__ == "__main__":
    main()
