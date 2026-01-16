#!/usr/bin/env python3
"""
Setup script for ScopeSignal
Run this to verify your environment is configured correctly.
"""

import os
import sys


def check_python_version():
    """Verify Python 3.8+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        print(f"   Current: Python {version.major}.{version.minor}")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_api_key():
    """Verify API key is configured"""
    key = os.getenv("DEEPSEEK_API_KEY")
    if not key:
        print("❌ DEEPSEEK_API_KEY not set")
        print("   1. Copy .env.example to .env")
        print("   2. Add your API key from https://platform.deepseek.com/api_keys")
        print("   3. Run: source .env (or set in your shell)")
        return False
    print("✓ API key configured")
    return True


def check_dependencies():
    """Verify required packages are installed"""
    try:
        import openai
        print(f"✓ openai {openai.__version__}")
        return True
    except ImportError:
        print("❌ openai package not installed")
        print("   Run: pip install -r requirements.txt")
        return False


def run_quick_test():
    """Run a single classification to verify everything works"""
    print("\n" + "="*60)
    print("Running quick test...")
    print("="*60 + "\n")
    
    try:
        from classifier import classify_update
        
        result = classify_update(
            update_text="Amendment 2 issued. See updated Attachment B.",
            trade="Electrical"
        )
        
        print("Test update: 'Amendment 2 issued. See updated Attachment B.'")
        print(f"Trade: Electrical")
        print(f"\nResult:")
        print(f"  Classification: {result['classification']}")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Reasoning: {result['reasoning']}")
        print(f"  Risk: {result['risk_note']}")
        
        if result['classification'] == 'CLOSED':
            print("\n✓ Test passed - system correctly identified administrative noise")
            return True
        else:
            print(f"\n⚠ Unexpected classification: {result['classification']}")
            print("  System may be too optimistic - review prompt")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Run all setup checks"""
    print("\n" + "="*60)
    print("SCOPESIGNAL - SETUP CHECK")
    print("="*60 + "\n")
    
    checks = [
        ("Python version", check_python_version),
        ("Dependencies", check_dependencies),
        ("API key", check_api_key),
    ]
    
    all_passed = True
    for name, check_fn in checks:
        print(f"Checking {name}...")
        if not check_fn():
            all_passed = False
        print()
    
    if not all_passed:
        print("❌ Setup incomplete - fix errors above\n")
        return 1
    
    print("✓ All checks passed\n")
    
    # Run quick test if all checks passed
    if run_quick_test():
        print("\n" + "="*60)
        print("SETUP COMPLETE")
        print("="*60)
        print("\nNext steps:")
        print("  1. Run evaluation: python -m evaluation.evaluate --quick")
        print("  2. Review results and mismatches")
        print("  3. Test with your own agency data")
        print()
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
