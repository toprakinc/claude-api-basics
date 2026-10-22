from pydantic import BaseModel, ValidationError

class Invoice(BaseModel):
    vendor: str
    total: float
    currency: str

good = Invoice(vendor="Acme Ltd", total="120.50", currency="USD")
print(good)

try:
    bad = Invoice(vendor="Acme Ltd", total="abc", currency="USD")
except ValidationError as e:
    print("Validation failed:")
    print(e)
    