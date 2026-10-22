import os
from dotenv import load_dotenv
from anthropic import Anthropic
from pydantic import BaseModel, ValidationError

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

class LineItem(BaseModel):
    description: str
    quantity: int
    unit_price: float

class Invoice(BaseModel):
    vendor: str
    total: float
    currency: str
    items: list[LineItem]

invoice_text = """
ACME LTD - Invoice #4471
Date: 03/10/2026
2x Office chair ..... 150 EUR
1x Desk ............. 89.90 EUR
TOTAL DUE: 389.90 EUR
"""

prompt = f"""Extract data from this invoice.
Return ONLY a JSON object with keys: vendor (string), total (number), currency (3-letter code), items (list of objects with description, quantity, unit_price).
Invoice:
{invoice_text}"""

response = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=500,
    messages=[{"role": "user", "content": prompt}],
)

raw = ""
for block in response.content:
    if block.type == "text":
        raw += block.text

print("Raw reply:", raw)
raw = raw.strip()
if raw.startswith("```"):
    raw = raw.split("\n", 1)[1]
    raw = raw.rsplit("```", 1)[0]

try:
    invoice = Invoice.model_validate_json(raw)
    print("Valid invoice:", invoice)
    calculated = sum(item.quantity * item.unit_price for item in invoice.items)
    print("Calculated total:", calculated)
    if abs(calculated - invoice.total) > 0.01:
        print("WARNING: total does not match line items!")
except ValidationError as e:
    print("Validation failed:")
    print(e)