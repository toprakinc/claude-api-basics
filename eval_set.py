# Test questions for the StepUp help center RAG.
# "expected" is an exact phrase from the PDF that must appear in the retrieved chunks.

EVAL_SET = [
    # Questions that use the same words as the document
    {"question": "How much does shipping cost?", "expected": "$5.99"},
    {
        "question": "How long does delivery take in the US?",
        "expected": "2-4 business days",
    },
    {
        "question": "Which payment methods do you accept?",
        "expected": "Visa, Mastercard",
    },
    {
        "question": "Can I exchange shoes for a different size?",
        "expected": "different size or color",
    },
    {"question": "How long do refunds take?", "expected": "5-7 business days"},
    {"question": "What is the support email?", "expected": "support@stepup.example"},
    {"question": "Do your shoes run true to size?", "expected": "true to size"},
    # Questions that use different words than the document
    {"question": "Can I send back sneakers I already wore?", "expected": "unworn"},
    {
        "question": "How long until my package arrives if I live in Germany?",
        "expected": "5-10 business days",
    },
    {
        "question": "Is there a fee if I mail my order back for my money?",
        "expected": "$4.99 for refunds",
    },
    {
        "question": "Can I split my payment into smaller parts?",
        "expected": "4 interest-free installments",
    },
    {
        "question": "Can I throw my sneakers in the washer?",
        "expected": "washing machine",
    },
    {
        "question": "I'm between two sizes, which one should I pick?",
        "expected": "larger size",
    },
    {
        "question": "How quickly will someone answer my message?",
        "expected": "within 24 hours",
    },
    {
        "question": "Which courier companies deliver your orders?",
        "expected": "UPS and DHL",
    },
]
