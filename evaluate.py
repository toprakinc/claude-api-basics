from eval_set import EVAL_SET
from rag import chunk_text, load_pdf_text, search_chunks

text = load_pdf_text("help_center.pdf")
chunks = chunk_text(text)

hits = 0
for item in EVAL_SET:
    question = item["question"]
    expected = item["expected"]
    results = search_chunks(question, chunks)
    # Join the top chunks and check if the expected phrase is anywhere in them
    found_text = " ".join(results)
    if expected.lower() in found_text.lower():
        hits += 1
        print("PASS", question)
    else:
        print("FAIL", question)

print(f"Score: {hits}/{len(EVAL_SET)}")
