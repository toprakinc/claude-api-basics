import os
from dotenv import load_dotenv
from anthropic import Anthropic
from pydantic import BaseModel, ValidationError

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODEL = "claude-haiku-5-5"


class LineItem(BaseModel):
    description: str
    quantity: int
    unit_price: float


class Invoice(BaseModel):
    vendor: str
    total: float
    currency: str
    items: list[LineItem]


def extract_invoice(invoice_text):
    """Send invoice text to Claude and return a validated Invoice, or None."""
    prompt = f"""Extract data from this invoice.
Return ONLY a JSON object with keys: vendor (string), total (number), currency (3-letter code), items (list of objects with description, quantity, unit_price).
No explanation, no markdown.

Invoice:
{invoice_text}"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    if response.stop_reason == "max_tokens":
        print("  ERROR: reply was cut off, increase max_tokens")
        return None

    raw = ""
    for block in response.content:
        if block.type == "text":
            raw += block.text

    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0]

    try:
        return Invoice.model_validate_json(raw)
    except ValidationError as e:
        print("  Validation failed:", e)
        return None


for filename in sorted(os.listdir("invoices")):
    if not filename.endswith(".txt"):
        continue

    print(f"\n=== {filename} ===")
    with open(os.path.join("invoices", filename)) as f:
        invoice_text = f.read()

    invoice = extract_invoice(invoice_text)
    if invoice is None:
        continue

    calculated = sum(item.quantity * item.unit_price for item in invoice.items)
    print(f"  Vendor: {invoice.vendor}")
    print(f"  Total: {invoice.total} {invoice.currency} | Calculated: {calculated:.2f}")
    if abs(calculated - invoice.total) > 0.01:
        print("  WARNING: total does not match line items!")
    else:
        print("  OK")