#!/usr/bin/env python3
"""
ScopeSignal CLI Tool
Command-line interface for classifying construction project updates.

Usage:
    # Single update
    python -m cli classify "Amendment 2 issued" --trade Electrical
    
    # Batch from file
    python -m cli batch input.json --output results.csv
    
    # Cache management
    python -m cli cache stats
    python -m cli cache clear
"""

import sys
import json
import argparse
from pathlib import Path

from classifier import (
    ScopeSignalClassifier, 
    ClassificationError,
    export_to_csv,
    export_to_json,
    export_summary_report
)


def cmd_classify(args):
    """Classify a single update"""
    try:
        classifier = ScopeSignalClassifier()
        result = classifier.classify_update(args.text, args.trade)
        
        print(f"\n{'='*60}")
        print("CLASSIFICATION RESULT")
        print('='*60)
        print(f"\nText: {args.text}")
        print(f"Trade: {args.trade}")
        print(f"\nClassification: {result['classification']}")
        print(f"Confidence: {result['confidence']}")
        print(f"\nReasoning: {result['reasoning']}")
        print(f"Risk Note: {result['risk_note']}")
        print(f"Recommended Action: {result['recommended_action']}")
        
        if result.get('_metadata', {}).get('cache_hit'):
            print(f"\n(Result from cache)")
        
        if args.json:
            print(f"\n{'='*60}")
            print("JSON OUTPUT")
            print('='*60)
            print(json.dumps(result, indent=2))
        
    except ClassificationError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_batch(args):
    """Classify multiple updates from file"""
    # Load input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(input_path, 'r') as f:
            if input_path.suffix == '.json':
                data = json.load(f)
                # Handle both array and object with "updates" key
                if isinstance(data, dict) and "updates" in data:
                    updates = data["updates"]
                elif isinstance(data, list):
                    updates = data
                else:
                    print("Error: JSON must be array or object with 'updates' key", file=sys.stderr)
                    sys.exit(1)
            else:
                print("Error: Only JSON input files supported", file=sys.stderr)
                sys.exit(1)
        
        # Validate updates format
        for i, update in enumerate(updates):
            if "text" not in update or "trade" not in update:
                print(f"Error: Update {i} missing 'text' or 'trade' field", file=sys.stderr)
                sys.exit(1)
        
        print(f"Loaded {len(updates)} updates from {args.input}")
        
        # Classify
        classifier = ScopeSignalClassifier()
        results = classifier.classify_batch(updates, show_progress=not args.quiet)
        
        # Export results
        output_path = Path(args.output)
        
        if output_path.suffix == '.csv':
            export_to_csv(results, args.output, include_metadata=args.include_metadata)
        elif output_path.suffix == '.json':
            export_to_json(results, args.output, include_metadata=args.include_metadata)
        else:
            print("Error: Output format must be .csv or .json", file=sys.stderr)
            sys.exit(1)
        
        # Generate summary if requested
        if args.summary:
            summary_path = output_path.with_suffix('.txt')
            export_summary_report(results, str(summary_path))
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_cache(args):
    """Manage cache"""
    from classifier.cache import ResultCache
    
    cache = ResultCache()
    
    if args.action == 'stats':
        stats = cache.stats()
        print(f"\n{'='*60}")
        print("CACHE STATISTICS")
        print('='*60)
        print(f"\nEntries: {stats['entries']}")
        print(f"Size: {stats['size_bytes']:,} bytes ({stats['size_bytes']/1024:.1f} KB)")
        
        if stats['entries'] > 0:
            print(f"Oldest entry: {stats['oldest_age_seconds']} seconds ago")
            print(f"Newest entry: {stats['newest_age_seconds']} seconds ago")
    
    elif args.action == 'clear':
        count = cache.clear()
        print(f"Cleared {count} cache entries")
    
    else:
        print(f"Unknown cache action: {args.action}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="ScopeSignal - Conservative construction project update classifier",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Classify single update
  %(prog)s classify "RFP issued for electrical work" --trade Electrical
  
  # Batch process from JSON file
  %(prog)s batch updates.json --output results.csv --summary
  
  # Check cache stats
  %(prog)s cache stats
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Classify command
    classify_parser = subparsers.add_parser('classify', help='Classify a single update')
    classify_parser.add_argument('text', help='Update text to classify')
    classify_parser.add_argument('--trade', required=True, 
                                 choices=['Electrical', 'HVAC', 'Plumbing'],
                                 help='Trade category')
    classify_parser.add_argument('--json', action='store_true',
                                 help='Output full JSON result')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Classify multiple updates from file')
    batch_parser.add_argument('input', help='Input JSON file with updates')
    batch_parser.add_argument('--output', '-o', required=True,
                             help='Output file (.csv or .json)')
    batch_parser.add_argument('--summary', action='store_true',
                             help='Generate summary report')
    batch_parser.add_argument('--include-metadata', action='store_true',
                             help='Include metadata in output')
    batch_parser.add_argument('--quiet', '-q', action='store_true',
                             help='Suppress progress output')
    
    # Cache command
    cache_parser = subparsers.add_parser('cache', help='Manage cache')
    cache_parser.add_argument('action', choices=['stats', 'clear'],
                             help='Cache action to perform')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Route to command handler
    if args.command == 'classify':
        cmd_classify(args)
    elif args.command == 'batch':
        cmd_batch(args)
    elif args.command == 'cache':
        cmd_cache(args)


if __name__ == '__main__':
    main()
