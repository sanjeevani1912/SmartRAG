# 15 Test Questions across all three query types, 5 per type.
# For each, we define the expected type and the expected ground truth / behavior.

TEST_QUESTIONS = [
    # ---- FACTUAL (5) ----
    {
        "query": "What is the penalty for violating prohibited system rules under the EU AI Act?",
        "expected_type": "factual",
        "ground_truth": "Up to 35 million euros or 7% of global turnover."
    },
    {
        "query": "What computational threshold defines a frontier model under the US Executive Order?",
        "expected_type": "factual",
        "ground_truth": "Computational resources exceeding 10^26 floating point operations."
    },
    {
        "query": "When did China's generative AI regulations come into force?",
        "expected_type": "factual",
        "ground_truth": "August 2023."
    },
    {
        "query": "What risk category do chatbots fall under in the EU AI Act?",
        "expected_type": "factual",
        "ground_truth": "Limited Risk (transparency obligations)."
    },
    {
        "query": "Which agencies does the US Executive Order direct to develop AI guidelines?",
        "expected_type": "factual",
        "ground_truth": "FTC, EEOC, NIST, OCC, CFPB."
    },
    
    # ---- SYNTHESIS (5) ----
    {
        "query": "How do the EU, US, and China differ in their approach to AI regulation?",
        "expected_type": "synthesis",
        "ground_truth": "EU uses a risk-based classification (AI Act). US uses a sectoral approach and executive orders (voluntary/industry focus). China uses targeted regulations for generative AI (security assessments)."
    },
    {
        "query": "What documentation must high-risk AI systems maintain, and what penalties apply if they fail compliance?",
        "expected_type": "synthesis",
        "ground_truth": "Documentation: system description, training data, validation/testing, human oversight, cybersecurity. Penalties: 15M euros or 3% global turnover (or 35M/7% for prohibited)."
    },
    {
        "query": "How does the EU AI Act treat open-source AI models compared to the US position?",
        "expected_type": "synthesis",
        "ground_truth": "EU has limited exemptions for open source (contested). US has been more permissive toward open source development."
    },
    {
        "query": "What are the transparency requirements for AI systems across different regulatory frameworks?",
        "expected_type": "synthesis",
        "ground_truth": "EU: chatbots/deepfakes must label. China: AI-content must be labeled. General themes include human oversight and interacting transparency."
    },
    {
        "query": "What concerns do industry groups have about the EU AI Act's implementation?",
        "expected_type": "synthesis",
        "ground_truth": "Ambiguity in high-risk categories (HR/recruitment), high compliance costs ($2M-$200M), and slowing innovation."
    },

    # ---- OUT OF SCOPE (5) ----
    {
        "query": "What is the EU AI Act's stance on AI-generated music?",
        "expected_type": "out_of_scope",
        "ground_truth": "Information not available."
    },
    {
        "query": "How does India regulate artificial intelligence?",
        "expected_type": "out_of_scope",
        "ground_truth": "Information not available."
    },
    {
        "query": "What specific watermarking technologies are approved under the US Executive Order?",
        "expected_type": "out_of_scope",
        "ground_truth": "Information not available."
    },
    {
        "query": "What penalties does Canada impose for AI violations?",
        "expected_type": "out_of_scope",
        "ground_truth": "Information not available."
    },
    {
        "query": "Does the EU AI Act cover AI systems used in personal hobby projects?",
        "expected_type": "out_of_scope",
        "ground_truth": "Information not available."
    }
]
