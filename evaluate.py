from eval_set import EVAL_SET
from rag import (
    HEADINGS,
    chunk_by_headings,
    embed_chunks,
    embed_queries,
    load_pdf_text,
    search_by_vector,
    search_chunks,
)

text = load_pdf_text("help_center.pdf")
chunks = chunk_by_headings(text, HEADINGS)
# Embed all chunks once (request 1)
chunk_vectors = embed_chunks(chunks)

# Collect all questions and embed them together (request 2)
questions = []
for item in EVAL_SET:
    questions.append(item["question"])
question_vectors = embed_queries(questions)

keyword_hits = 0
semantic_hits = 0
for item, question_vector in zip(EVAL_SET, question_vectors):
    question = item["question"]
    expected = item["expected"].lower()

    keyword_text = " ".join(search_chunks(question, chunks, k=1)).lower()
    semantic_text = " ".join(
        search_by_vector(question_vector, chunks, chunk_vectors, k=1)
    ).lower()

    if expected in keyword_text:
        keyword_hits += 1
        keyword_result = "PASS"
    else:
        keyword_result = "FAIL"

    if expected in semantic_text:
        semantic_hits += 1
        semantic_result = "PASS"
    else:
        semantic_result = "FAIL"

    print(f"keyword: {keyword_result} | semantic: {semantic_result} | {question}")

print(f"\nKeyword search:  {keyword_hits}/{len(EVAL_SET)}")
print(f"Semantic search: {semantic_hits}/{len(EVAL_SET)}")
