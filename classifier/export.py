"""
Export utilities for classification results.
Supports CSV and JSON formats for manual review and analysis.
"""

import csv
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


def export_to_csv(
    results: List[Dict],
    output_path: str,
    include_metadata: bool = False
) -> None:
    """
    Export classification results to CSV format.
    
    Args:
        results: List of classification result dicts
        output_path: Path to output CSV file
        include_metadata: Whether to include _metadata fields
    """
    if not results:
        raise ValueError("No results to export")
    
    # Determine columns based on first result
    base_columns = [
        "update_id",
        "text",
        "trade",
        "classification",
        "confidence",
        "reasoning",
        "risk_note",
        "recommended_action",
        "trade_relevant"
    ]
    
    # Create output directory if needed
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        # Prepare columns
        columns = base_columns.copy()
        
        if include_metadata:
            # Add common metadata fields
            meta_fields = ["model", "latency_ms", "cache_hit", "provider"]
            columns.extend([f"meta_{field}" for field in meta_fields])
        
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        
        for result in results:
            row = {}
            
            # Copy base fields
            for col in base_columns:
                row[col] = result.get(col, "")
            
            # Extract metadata if requested
            if include_metadata and "_metadata" in result:
                meta = result["_metadata"]
                for field in ["model", "latency_ms", "cache_hit", "provider"]:
                    row[f"meta_{field}"] = meta.get(field, "")
            
            writer.writerow(row)
    
    print(f"Exported {len(results)} results to {output_path}")


def export_to_json(
    results: List[Dict],
    output_path: str,
    pretty: bool = True,
    include_metadata: bool = True
) -> None:
    """
    Export classification results to JSON format.
    
    Args:
        results: List of classification result dicts
        output_path: Path to output JSON file
        pretty: Whether to format with indentation
        include_metadata: Whether to include _metadata fields
    """
    if not results:
        raise ValueError("No results to export")
    
    # Create output directory if needed
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Clean results if metadata not wanted
    if not include_metadata:
        results = [
            {k: v for k, v in r.items() if not k.startswith("_")}
            for r in results
        ]
    
    # Add export metadata
    export_data = {
        "exported_at": datetime.now().isoformat(),
        "total_results": len(results),
        "results": results
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2 if pretty else None)
    
    print(f"Exported {len(results)} results to {output_path}")


def export_summary_report(
    results: List[Dict],
    output_path: str
) -> None:
    """
    Export a summary report of classification results.
    
    Args:
        results: List of classification result dicts
        output_path: Path to output text file
    """
    if not results:
        raise ValueError("No results to export")
    
    # Calculate statistics
    total = len(results)
    classifications = {}
    confidences = []
    errors = 0
    
    for result in results:
        classification = result.get("classification", "UNKNOWN")
        classifications[classification] = classifications.get(classification, 0) + 1
        
        if classification == "ERROR":
            errors += 1
        elif "confidence" in result:
            confidences.append(result["confidence"])
    
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    
    # Create output directory if needed
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Write report
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("SCOPESIGNAL CLASSIFICATION REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write(f"Total Updates: {total}\n")
        f.write(f"Successful: {total - errors}\n")
        f.write(f"Errors: {errors}\n\n")
        
        f.write("Classification Distribution:\n")
        for classification, count in sorted(classifications.items()):
            pct = count / total * 100
            f.write(f"  {classification}: {count} ({pct:.1f}%)\n")
        
        f.write(f"\nAverage Confidence: {avg_confidence:.1f}\n\n")
        
        f.write("=" * 60 + "\n\n")
        
        # List contestable opportunities (the rare valuable ones)
        contestable = [r for r in results if r.get("classification") == "CONTESTABLE"]
        if contestable:
            f.write(f"CONTESTABLE OPPORTUNITIES ({len(contestable)})\n")
            f.write("-" * 60 + "\n\n")
            for r in contestable:
                f.write(f"Trade: {r.get('trade', 'N/A')}\n")
                f.write(f"Text: {r.get('text', 'N/A')}\n")
                f.write(f"Confidence: {r.get('confidence', 0)}\n")
                f.write(f"Reasoning: {r.get('reasoning', 'N/A')}\n")
                f.write(f"Next Action: {r.get('recommended_action', 'N/A')}\n\n")
    
    print(f"Summary report saved to {output_path}")


if __name__ == "__main__":
    # Quick test
    test_results = [
        {
            "update_id": "test_1",
            "text": "Amendment 2 issued",
            "trade": "Electrical",
            "classification": "CLOSED",
            "confidence": 95,
            "reasoning": "Administrative noise",
            "risk_note": "Could contain hidden scope",
            "recommended_action": "Monitor for follow-ups",
            "trade_relevant": True,
            "_metadata": {
                "model": "deepseek-chat",
                "latency_ms": 450,
                "cache_hit": False
            }
        },
        {
            "update_id": "test_2",
            "text": "RFP issued for electrical work",
            "trade": "Electrical",
            "classification": "CONTESTABLE",
            "confidence": 80,
            "reasoning": "Clear RFP with deadline",
            "risk_note": "May be prequalified vendors only",
            "recommended_action": "Submit proposal immediately",
            "trade_relevant": True,
            "_metadata": {
                "model": "deepseek-chat",
                "latency_ms": 520,
                "cache_hit": False
            }
        }
    ]
    
    # Test exports
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = f"{tmpdir}/results.csv"
        json_path = f"{tmpdir}/results.json"
        report_path = f"{tmpdir}/report.txt"
        
        export_to_csv(test_results, csv_path, include_metadata=True)
        export_to_json(test_results, json_path)
        export_summary_report(test_results, report_path)
        
        print("✓ Export tests passed")
