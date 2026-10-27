from pypdf import PdfReader

reader = PdfReader("help_center.pdf")

text = ""
for page in reader.pages:
    # Each page extracts its own text; we collect them all in one string
    text += page.extract_text()

print(text)
