from pypdf import PdfReader


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


if __name__ == "__main__":
    text = load_pdf_text("help_center.pdf")
    chunks = chunk_text(text)
    print(len(chunks))
    print(chunks[0])
