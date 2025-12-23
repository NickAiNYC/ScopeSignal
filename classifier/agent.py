"""
ScopeSignal Classifier - Core Agent
Applies veteran subcontractor judgment to construction project updates.
Conservative by design. Trust comes from restraint, not optimism.

Switched to DeepSeek API (OpenAI-compatible) - lower cost, comparable quality.
"""

import os
import json
import time
import hashlib
from typing import Dict, Literal
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# The hardened prompt - DO NOT MODIFY without documented reason
SYSTEM_PROMPT = """You are a NYC construction subcontractor with 20+ years of field and bidding experience.
You have personally seen how public agencies disguise real work inside administrative language.
Your task:
Analyze a single project update for ONE specified trade (Electrical, HVAC, Plumbing).
You must think like a veteran operator, not an AI.

STEP 1 — Trade Relevance Gate
Determine whether this update contains work that is materially relevant to the specified trade.
If not relevant, STOP and classify as CLOSED.

STEP 2 — Opportunity Reality Check
Assess whether the update represents:
- Administrative noise
- Politically or contractually earmarked work
- Softly opened scope with a favored incumbent
- Truly contestable, bid-able work

STEP 3 — Classification
Classify as EXACTLY ONE:
1. CLOSED – No realistic opportunity for a new subcontractor
2. SOFT_OPEN – New scope exists but incumbent or insider advantage likely
3. CONTESTABLE – Clearly defined, openly bid-able work

STEP 4 — Risk Awareness
Identify what could make your judgment wrong (missing attachments, agency behavior, incumbency).

STRICT RULES:
- Do NOT be optimistic.
- When uncertain, downgrade classification.
- Assume agencies prefer incumbents unless language proves otherwise.
- Confidence must reflect how a real contractor would bet time and money.

Respond ONLY in valid JSON:
{
  "trade_relevant": true | false,
  "classification": "CLOSED" | "SOFT_OPEN" | "CONTSTABLE",
  "confidence": 0-100,
  "reasoning": "One blunt sentence explaining the decision.",
  "risk_note": "One reason this classification could be wrong.",
  "recommended_action": "One concrete next step a subcontractor should take."
}"""


class ClassificationError(Exception):
    """Raised when classification fails after retries"""
    pass


class ScopeSignalClassifier:
    """
    Conservative classifier for construction project updates.
    Designed to minimize false positives and wasted contractor time.
    
    Backend: DeepSeek (OpenAI-compatible API) - cost-effective alternative to Claude
    """
    
    def __init__(self, api_key: str = None, max_retries: int = 3):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY must be set in environment or passed directly")
        
        # Initialize OpenAI client configured for DeepSeek
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
        self.max_retries = max_retries
        self.model = "deepseek-chat"  # Options: "deepseek-chat" or "deepseek-reasoner"
    
    def _cache_key(self, update_text: str, trade: str) -> str:
        """
        Generate deterministic cache key for update + trade combination.
        Enables future caching without changing interface.
        """
        raw = f"{trade}:{update_text}".encode()
        return hashlib.sha256(raw).hexdigest()
    
    def _call_llm(self, system_prompt: str, user_message: str) -> str:
        """
        Abstract LLM call to single method.
        Makes backend swapping trivial - only this method needs changing.
        
        Args:
            system_prompt: System instructions
            user_message: User query
            
        Returns:
            Raw text response from LLM
            
        Raises:
            Exception: On API errors (caller handles retries)
        """
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=1000,
            temperature=0.1,  # Low temperature for consistent, conservative outputs
            response_format={"type": "json_object"},  # Critical: Forces JSON output
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content.strip()
    
    def _validate_schema_invariants(self, result: Dict) -> None:
        """
        Enforce domain constraints beyond basic schema validation.
        These encode contractor psychology and logical consistency.
        
        Raises:
            ValueError: When domain constraints are violated
        """
        # CRITICAL FIX #1: Enforce trade_relevant consistency
        # If not trade-relevant, classification MUST be CLOSED
        if not result["trade_relevant"] and result["classification"] != "CLOSED":
            raise ValueError(
                f"Invalid output: trade_relevant=false must imply classification=CLOSED, "
                f"got classification={result['classification']}"
            )
        
        # CRITICAL FIX #2: Confidence ceilings by classification
        # These encode contractor psychology - contestable work is rare and uncertain
        classification = result["classification"]
        confidence = result["confidence"]
        
        if classification == "CONTESTABLE" and confidence > 85:
            raise ValueError(
                f"CONTESTABLE confidence unrealistically high: {confidence}. "
                f"Real contractors never bet with >85% confidence on open competition."
            )
        
        if classification == "SOFT_OPEN" and confidence > 75:
            raise ValueError(
                f"SOFT_OPEN confidence unrealistically high: {confidence}. "
                f"Ambiguous signals should reflect uncertainty."
            )
    
    def classify_update(
        self, 
        update_text: str, 
        trade: Literal["Electrical", "HVAC", "Plumbing"]
    ) -> Dict:
        """
        Classify a single project update for a specified trade.
        
        Args:
            update_text: Raw text from agency notice/bulletin/change order
            trade: One of "Electrical", "HVAC", "Plumbing"
        
        Returns:
            Dict with keys: trade_relevant, classification, confidence, 
                           reasoning, risk_note, recommended_action
        
        Raises:
            ClassificationError: If classification fails after retries
        """
        if trade not in ["Electrical", "HVAC", "Plumbing"]:
            raise ValueError(f"Invalid trade: {trade}. Must be Electrical, HVAC, or Plumbing")
        
        user_message = f"Trade: {trade}\n\nProject Update:\n{update_text}"
        
        # Generate cache key (not used yet, but ready for caching implementation)
        cache_key = self._cache_key(update_text, trade)
        
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                
                # Use abstracted LLM call
                response_text = self._call_llm(SYSTEM_PROMPT, user_message)
                
                # DeepSeek already returns clean JSON due to response_format parameter
                # Remove this handling if you find DeepSeek doesn't wrap in markdown
                if response_text.startswith("```"):
                    response_text = response_text.split("```")[1]
                    if response_text.startswith("json"):
                        response_text = response_text[4:]
                    response_text = response_text.strip()
                
                result = json.loads(response_text)
                
                # Validate required fields
                required_fields = [
                    "trade_relevant", "classification", "confidence",
                    "reasoning", "risk_note", "recommended_action"
                ]
                
                for field in required_fields:
                    if field not in result:
                        raise ValueError(f"Missing required field: {field}")
                
                # Validate classification value
                valid_classifications = ["CLOSED", "SOFT_OPEN", "CONTESTABLE"]
                if result["classification"] not in valid_classifications:
                    raise ValueError(f"Invalid classification: {result['classification']}")
                
                # Validate confidence range
                if not isinstance(result["confidence"], (int, float)) or not (0 <= result["confidence"] <= 100):
                    raise ValueError(f"Confidence must be 0-100, got: {result['confidence']}")
                
                # CRITICAL: Enforce domain-specific schema invariants
                self._validate_schema_invariants(result)
                
                # Calculate latency
                latency_ms = int((time.time() - start_time) * 1000)
                
                # Add metadata
                result["_metadata"] = {
                    "trade": trade,
                    "model": self.model,
                    "attempt": attempt + 1,
                    "latency_ms": latency_ms,
                    "cache_key": cache_key,
                    "provider": "deepseek"
                }
                
                # Add downgrade reason if applicable
                if not result["trade_relevant"]:
                    result["_metadata"]["downgrade_reason"] = "trade_irrelevant"
                elif result["classification"] == "CLOSED":
                    # Check if reasoning suggests ambiguity-driven downgrade
                    reasoning_lower = result["reasoning"].lower()
                    if any(word in reasoning_lower for word in ["unclear", "ambiguous", "missing", "vague", "uncertain"]):
                        result["_metadata"]["downgrade_reason"] = "ambiguous_language"
                
                return result
                
            except json.JSONDecodeError as e:
                if attempt == self.max_retries - 1:
                    raise ClassificationError(f"Failed to parse JSON after {self.max_retries} attempts: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise ClassificationError(f"Classification failed after {self.max_retries} attempts: {e}")
                time.sleep(2 ** attempt)
        
        raise ClassificationError("Unexpected retry loop exit")


def classify_update(
    update_text: str,
    trade: Literal["Electrical", "HVAC", "Plumbing"],
    api_key: str = None
) -> Dict:
    """
    Convenience function for one-off classifications.
    
    Usage:
        result = classify_update("Amendment 2 issued. See Attachment B.", "Electrical")
        print(result["classification"])  # "CLOSED"
    """
    classifier = ScopeSignalClassifier(api_key=api_key)
    return classifier.classify_update(update_text, trade)


if __name__ == "__main__":
    # Manual sanity test with hardcoded examples
    test_cases = [
        {
            "text": "Amendment 2 issued. See updated Attachment B.",
            "trade": "Electrical",
            "expected": "CLOSED"
        },
        {
            "text": "RFP issued for additional electrical work. Qualified vendors may submit pricing by March 15.",
            "trade": "Electrical", 
            "expected": "CONTESTABLE"
        },
        {
            "text": "Change order executed to address unforeseen conditions.",
            "trade": "HVAC",
            "expected": "SOFT_OPEN"
        },
        {
            "text": "Agency evaluating additional mechanical work pending funding.",
            "trade": "HVAC",
            "expected": "SOFT_OPEN"
        },
        {
            "text": "Revised scope for plumbing fixtures - see meeting notes.",
            "trade": "Plumbing",
            "expected": "SOFT_OPEN"  # Missing context = downgrade
        }
    ]
    
    print("Running manual sanity tests with DeepSeek backend...\n")
    
    try:
        classifier = ScopeSignalClassifier()
        print("✓ DeepSeek client initialized successfully\n")
    except ValueError as e:
        print(f"✗ Setup failed: {e}")
        print("\nTo fix:")
        print("1. Get a DeepSeek API key from https://platform.deepseek.com/api_keys")
        print("2. Set DEEPSEEK_API_KEY environment variable:")
        print("   export DEEPSEEK_API_KEY='your_key_here'")
        print("   # Or add to .env file: DEEPSEEK_API_KEY=your_key_here")
        exit(1)
    
    for i, case in enumerate(test_cases, 1):
        print(f"TEST {i}/{len(test_cases)}")
        print(f"Trade: {case['trade']}")
        print(f"Text: {case['text']}")
        print(f"Expected: {case['expected']}")
        
        try:
            result = classifier.classify_update(case['text'], case['trade'])
            print(f"Got: {result['classification']} (confidence: {result['confidence']})")
            print(f"Reasoning: {result['reasoning']}")
            print(f"Risk: {result['risk_note']}")
            
            match = "✓ MATCH" if result['classification'] == case['expected'] else "✗ MISMATCH"
            print(f"{match}\n")
            
        except Exception as e:
            print(f"✗ ERROR: {e}\n")
