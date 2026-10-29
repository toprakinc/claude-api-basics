from pypdf import PdfReader
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()
MODEL = "claude-haiku-5-5"


def load_pdf_text(path):
    """Read every page of a PDF and return all text as one string."""
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        # Add a newline so the last word of one page doesn't stick to the next page
        text += page.extract_text() + "\n"
    return text


def chunk_text(text, chunk_size=80, overlap=20):
    """Split text into overlapping chunks of about chunk_size words."""
    words = text.split()
    chunks = []
    step = chunk_size - overlap
    for start in range(0, len(words), step):
        chunks.append(" ".join(words[start : start + chunk_size]))
        # Stop once this chunk reaches the end, so we don't make a tiny leftover chunk
        if start + chunk_size >= len(words):
            break
    return chunks


def search_chunks(question, chunks, k=3):
    """Return the k chunks that share the most words with the question."""
    question_words = (
        # Remove punctuation so "shoes?" matches "shoes"
        question.lower()
        .replace("?", "")
        .replace(".", "")
        .replace(",", "")
        .replace(";", "")
        .split()
    )

    scored = []
    for chunk in chunks:
        # Remove punctuation so "shoes?" matches "shoes"
        chunk_words = (
            chunk.lower()
            .replace("?", "")
            .replace(".", "")
            .replace(",", "")
            .replace(";", "")
            .split()
        )
        score = 0
        for word in question_words:
            if word in chunk_words:
                score += 1
        scored.append((score, chunk))
    scored = sorted(scored, reverse=True)
    results = []
    for score, chunk in scored[:k]:
        results.append(chunk)
    return results


def answer_question(question, chunks):
    top_chunks = search_chunks(question, chunks)

    # Join the chunks into one text, with a blank line between them
    context = "\n\n".join(top_chunks)
    prompt = f"""Answer the customer's question using only the documents below.
If the answer is not in the documents, say "I don't know".

Documents:
{context}

Question: {question}"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    reply = ""
    for block in response.content:
        if block.type == "text":
            reply += block.text
    return reply


if __name__ == "__main__":
    text = load_pdf_text("help_center.pdf")
    chunks = chunk_text(text)
    print(answer_question("How many days do I have to return shoes?", chunks))
    print("---")
    print(answer_question("Do you sell watches?", chunks))
