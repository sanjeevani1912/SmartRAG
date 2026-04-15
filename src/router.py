import os
import re

# Refined Synthesis Keywords & Phrases
SYNTHESIS_KEYWORDS = [
    "compare", "versus", "how do", "contrast", 
    "similarities", "different jurisdictions",
    "disagreement", "contradiction", "between",
    "across different", "requirements for",
    "concerns", "industry groups"
]

SYNTHESIS_PHRASES = [
    r"documentation.*penalties",
    r"maintain.*penalties",
    r"what are the",
    r"what concerns",
    r"what documentation"
]

# Explicit Out-of-Scope Intent Signals (Negative Selection)
# This allows us to lower the threshold safely.
OUT_OF_SCOPE_SIGNALS = [
    "india", "canada", "japan", "australia",
    "hobby", "personal use", "music", "approved technologies"
]

class SmartRouter:
    def __init__(self, threshold=0.42, synthesis_doc_threshold=4):
        """
        Threshold 0.42 selected to capture sparse technical signal (Frontier Model) 
        while relying on Negative Signals to block high-keyword noise (India/Canada).
        """
        self.threshold = threshold
        self.synthesis_doc_threshold = synthesis_doc_threshold
        self.last_decision = {}

    def calculate_confidence(self, max_score, decision):
        """Calculates a qualitative confidence score."""
        if decision == "out_of_scope":
            return "ZERO"
        elif max_score > 0.65:
            return "HIGH"
        elif max_score > 0.50:
            return "MEDIUM"
        else:
            return "LOW"

    def classify_query(self, query, retrieved_chunks, scores):
        """
        Hybrid routing: Score-based + Intent-based signals.
        """
        query_lower = query.lower()
        max_score = max(scores) if scores else 0
        sorted_scores = sorted(scores, reverse=True)
        score_gap = sorted_scores[0] - sorted_scores[1] if len(sorted_scores) > 1 else 1.0
        
        source_docs = set(chunk.metadata.get("source", "unknown") for chunk in retrieved_chunks)

        # Step 1: Negative Intent Signal Check
        has_oos_signal = any(sig in query_lower for sig in OUT_OF_SCOPE_SIGNALS)
        
        if has_oos_signal and max_score < 0.55:
            decision = "out_of_scope"
            reason = "Explicit out-of-scope intent signal detected with low/moderate confidence."
        
        # Step 2: Global Threshold Check
        elif max_score < self.threshold:
            decision = "out_of_scope"
            reason = f"Max similarity ({max_score:.3f}) below calibrated threshold ({self.threshold})."
        
        else:
            # Step 3: Synthesis Intent Check
            has_synthesis_keyword = any(kw in query_lower for kw in SYNTHESIS_KEYWORDS)
            has_synthesis_phrase = any(re.search(ph, query_lower) for ph in SYNTHESIS_PHRASES)

            if has_synthesis_keyword or has_synthesis_phrase:
                decision = "synthesis"
                reason = "Explicit synthesis intent detected in query structure/keywords."
            
            elif score_gap > 0.05 and len(source_docs) <= 3:
                # Factual dominance
                decision = "factual"
                reason = f"Strong primary chunk match (gap: {score_gap:.3f})."
            
            elif len(source_docs) >= self.synthesis_doc_threshold:
                # Deep crossing signal
                decision = "synthesis"
                reason = f"Information spread across {len(source_docs)} documents."
            
            else:
                decision = "factual"
                reason = "Defaulting to factual retrieval (no strong synthesis markers)."

        confidence = self.calculate_confidence(max_score, decision)

        self.last_decision = {
            "query": query,
            "type": decision,
            "confidence": confidence,
            "reason": reason,
            "max_score": max_score,
            "score_gap": score_gap,
            "source_docs": list(source_docs)
        }
        
        return decision, reason

    def get_logs(self):
        return self.last_decision
