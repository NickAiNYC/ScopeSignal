"""
Realistic Project Update Simulator
Generates deliberately ambiguous, noisy agency language.
If everything classifies cleanly, this simulator failed.
"""

import random
from typing import List, Dict, Literal


# Template categories - UGLY ON PURPOSE
TEMPLATES = {
    "administrative_noise": [
        "Amendment {num} issued. See updated Attachment {letter}.",
        "Field conditions reviewed. No cost impact anticipated.",
        "Clarification memo posted per GC request.",
        "Pre-bid meeting minutes available on project portal.",
        "Addendum {num} issued - typographical corrections only.",
        "Site visit scheduled for {date}. RSVP required.",
        "Document revision log updated. Review recommended.",
        "Contractor submittals under review by agency.",
    ],
    
    "incumbent_earmarked": [
        "Change order executed to address unforeseen conditions.",
        "Revised scope issued to current contractor for review.",
        "Additional work authorized under existing contract.",
        "Supplemental payment approved for contractor of record.",
        "Contract modification executed per field directive.",
        "Current vendor to provide pricing on add-on scope.",
        "Existing contractor awarded additional phase work.",
        "Time extension granted with associated cost adjustment.",
    ],
    
    "soft_open": [
        "Supplemental scope under review; alternates may be considered.",
        "Agency evaluating additional {trade} work pending funding.",
        "Add-on work identified; coordination ongoing.",
        "Potential {trade} scope expansion under discussion.",
        "Additional {trade} requirements may be issued pending approval.",
        "Supplementary work being considered for separate procurement.",
        "Agency reviewing options for expanded {trade} systems.",
        "Revised budget may allow for additional {trade} scope.",
    ],
    
    "contestable": [
        "RFP issued for additional {trade} work. Qualified vendors may submit pricing by {date}.",
        "Separate bid package released for added {trade} scope.",
        "Supplemental {trade} scope opened for competitive proposals.",
        "New {trade} contract solicitation posted. Bids due {date}.",
        "Competitive procurement initiated for {trade} system upgrades.",
        "Request for proposals: {trade} work not covered under base contract.",
        "Open bidding for supplemental {trade} installation. See project portal.",
        "Independent {trade} package available for qualified subcontractors.",
    ],
    
    "agency_weirdness": [
        "SCA Bulletin: Miscellaneous revisions per site conditions.",
        "DDC Notice: Scope clarification forthcoming.",
        "HPD Addendum: Cost proposal requested.",
        "NYCHA Advisory: Field coordination required for {trade} trades.",
        "DEP Notice: Environmental review may impact {trade} schedule.",
        "DOT Bulletin: Traffic management plan affects site access.",
        "Parks Dept: Historic preservation review in progress.",
        "DCAS Notice: Prevailing wage determination updated.",
    ],
    
    "missing_context": [
        "Scope revised — see drawings.",
        "Work added per meeting notes.",
        "Pricing adjustment requested.",
        "{trade} modifications required - details TBD.",
        "Refer to updated specifications for {trade} systems.",
        "Additional requirements per consultant review.",
        "See attached for scope changes.",
        "Revised {trade} scope per owner directive.",
        "Cost impact assessment needed for proposed changes.",
        "Contractor to provide input on feasibility.",
    ]
}


TRADES = ["electrical", "HVAC", "plumbing"]


def generate_update(
    category: str = None,
    trade: Literal["electrical", "HVAC", "plumbing"] = None,
    seed: int = None
) -> Dict:
    """
    Generate a single realistic project update.
    
    Args:
        category: Specific category to use, or None for random
        trade: Specific trade to inject, or None for random
        seed: Random seed for reproducibility
    
    Returns:
        Dict with 'text', 'category', 'trade' keys
    """
    if seed is not None:
        random.seed(seed)
    
    if category is None:
        category = random.choice(list(TEMPLATES.keys()))
    
    if category not in TEMPLATES:
        raise ValueError(f"Invalid category: {category}")
    
    template = random.choice(TEMPLATES[category])
    
    # Select trade
    if trade is None:
        trade = random.choice(TRADES)
    else:
        trade = trade.lower()
    
    # Fill in placeholders
    text = template
    text = text.replace("{trade}", trade)
    text = text.replace("{num}", str(random.randint(1, 9)))
    text = text.replace("{letter}", random.choice("ABCDEFG"))
    text = text.replace("{date}", f"March {random.randint(10, 31)}")
    
    return {
        "text": text,
        "category": category,
        "trade": trade,
        "expected_classification": _get_expected_classification(category)
    }


def _get_expected_classification(category: str) -> str:
    """Map category to expected classification (for validation)"""
    mapping = {
        "administrative_noise": "CLOSED",
        "incumbent_earmarked": "CLOSED",
        "soft_open": "SOFT_OPEN",
        "contestable": "CONTESTABLE",
        "agency_weirdness": "CLOSED",  # Ambiguous, should lean closed
        "missing_context": "CLOSED",  # Ambiguity = downgrade
    }
    return mapping.get(category, "CLOSED")


def generate_batch(
    count: int = 100,
    category_distribution: Dict[str, float] = None,
    seed: int = None
) -> List[Dict]:
    """
    Generate a batch of realistic updates with controlled distribution.
    
    Args:
        count: Number of updates to generate
        category_distribution: Dict mapping category to probability (must sum to 1.0)
        seed: Random seed for reproducibility
    
    Returns:
        List of update dicts
    """
    if seed is not None:
        random.seed(seed)
    
    # Default distribution reflects real-world rarity
    if category_distribution is None:
        category_distribution = {
            "administrative_noise": 0.30,
            "incumbent_earmarked": 0.25,
            "soft_open": 0.20,
            "agency_weirdness": 0.15,
            "missing_context": 0.08,
            "contestable": 0.02,  # RARE - this is the point
        }
    
    # Validate distribution
    total = sum(category_distribution.values())
    if not (0.99 <= total <= 1.01):  # Allow floating point tolerance
        raise ValueError(f"Category distribution must sum to 1.0, got {total}")
    
    # Generate weighted samples
    categories = list(category_distribution.keys())
    weights = list(category_distribution.values())
    
    updates = []
    for i in range(count):
        category = random.choices(categories, weights=weights)[0]
        update = generate_update(category=category, seed=None)
        update["id"] = f"update_{i+1:03d}"
        updates.append(update)
    
    return updates


def generate_adversarial_set() -> List[Dict]:
    """
    Generate specific edge cases designed to test classifier robustness.
    These should be hard to classify correctly.
    """
    adversarial_cases = [
        {
            "text": "RFP posted for electrical scope review.",
            "category": "missing_context",
            "trade": "electrical",
            "note": "Looks like 'RFP' but just for review, not bidding"
        },
        {
            "text": "Additional HVAC work authorized. Details pending.",
            "category": "missing_context",
            "trade": "HVAC",
            "note": "Authorized but unclear if incumbent or open"
        },
        {
            "text": "Competitive pricing requested for plumbing modifications.",
            "category": "soft_open",
            "trade": "plumbing",
            "note": "Sounds open but no deadline or clear process"
        },
        {
            "text": "Change order for electrical upgrades under consideration.",
            "category": "soft_open",
            "trade": "electrical",
            "note": "Change order = incumbent, but 'under consideration' = not approved"
        },
        {
            "text": "Separate bid package for HVAC work. See existing contractor for details.",
            "category": "incumbent_earmarked",
            "trade": "HVAC",
            "note": "Says 'separate bid' but 'see existing contractor' = rigged"
        }
    ]
    
    for i, case in enumerate(adversarial_cases):
        case["id"] = f"adversarial_{i+1}"
        case["expected_classification"] = _get_expected_classification(case["category"])
    
    return adversarial_cases


if __name__ == "__main__":
    print("=== Batch Generation Test ===\n")
    
    # Generate standard batch
    batch = generate_batch(count=20, seed=42)
    
    print(f"Generated {len(batch)} updates")
    print("\nCategory distribution:")
    
    category_counts = {}
    for update in batch:
        cat = update["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    for cat, count in sorted(category_counts.items()):
        print(f"  {cat}: {count}")
    
    print("\n=== Sample Updates ===\n")
    for update in batch[:5]:
        print(f"ID: {update['id']}")
        print(f"Text: {update['text']}")
        print(f"Category: {update['category']} → Expected: {update['expected_classification']}")
        print()
    
    print("=== Adversarial Set ===\n")
    adversarial = generate_adversarial_set()
    
    for case in adversarial:
        print(f"ID: {case['id']}")
        print(f"Text: {case['text']}")
        print(f"Note: {case['note']}")
        print(f"Expected: {case['expected_classification']}")
        print()
