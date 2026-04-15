# Failure Analysis: Engineering Logic vs. Retrieval Noise

SmartRAG achieved an overall **86.67% Routing Accuracy**. The remaining 13.3% (2 misrouted queries) and an inherent heuristic limitation provide significant engineering insights into the challenges of production RAG systems.

## 1. Multi-Document Fact Overlap (The "Frontier Model" Case)

### Case:
Query: *"What computational threshold defines a frontier model...?"* (**Expected: Factual, Predicted: Synthesis**).

### Analysis:
The threshold (10^26 FLOPs) is a single fact, but it appears in multiple contexts across Document 4 (Technical Brief) and is referenced in Document 2 (News Article). 

### Why it "Failed":
Our router uses a `synthesis_doc_threshold` of 4. While this query only hit 2 documents, it fell into the `synthesis` path because the **Score-Gap** was not high enough to override the multi-document retrieval. The router interpreted the presence of the fact in two different types of documents as a need for jurisdictional comparison rather than a single fact retrieval.

---

## 2. Semantic Broadness (The "Chatbots" Case)

### Case:
Query: *"What risk category do chatbots fall under in the EU AI Act?"* (**Expected: Factual, Predicted: Synthesis**).

### Analysis:
Because "chatbots" are a thematic center of multiple documents, the retrieval step returned high-quality chunks from almost every indexed source (Documents 1, 2, and 4).

### Why it "Failed":
The query triggered Rule 3: **Extensive Retrieval** (len(source_docs) >= 4). From a logical perspective, if a query returns relevant data from 4 different regulatory sources, it almost always requires synthesis. In this specific case, the fact (Limited Risk) was present in all of them, but the router prioritized the "broadness" signal, leading to a Synthesis classification.

---

## 3. Contradiction Detection Brittleness

### Case:
The `SmartGenerator.check_contradictions()` function handles the EU AI Act penalty discrepancy (30M vs 35M).

### Limitation:
Initially, this check relied on simple substring matching for the digits "30" and "35". In a production environment, this is brittle and prone to false positives (e.g., matching "Article 30", "Year 2030", or a "35% increase"). 

### Fix Implemented:
The system was upgraded to use anchored regex patterns (`\b30\s*million\b`, `\b35\s*million\b`). However, even this approach is a heuristic; a truly robust system would use a secondary LLM "Relational Evaluator" to verify if the $30M and $35M figures are actually being compared as penalties for the same violation.

---

## What Would Improve These Results

- **MPNet Embedding Model**: Upgrading from `all-MiniLM-L6-v2` to `all-mpnet-base-v2` would improve the semantic density of technical terms (like FLOPS), potentially increasing the **Score-Gap** for factual queries.
- **Dynamic Synthesis Thresholding**: Raising the `synthesis_doc_threshold` from 4 to 5 would reduce false synthesis triggers for factual queries whose content appears in multiple documents by coincidence.
- **LLM-Based Verification**: Using a small, fast model (like Llama-3-8B) as a "Router Validator" could double-check the rule-based decisions, combining the speed of heuristics with the nuance of language models.
