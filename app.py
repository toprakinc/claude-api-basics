from fastapi import FastAPI, HTTPException  # import the FastAPI class
from pydantic import BaseModel
from extract import extract_invoice

app = FastAPI()  # create the web app


class InvoiceText(BaseModel):
    text: str


@app.get("/")  # when someone visits the main address...
def home():  # ...run this function
    return {"message": "Invoice API is running"}  # send back JSON


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/extract")
def extract(data: InvoiceText):
    result = extract_invoice(data.text)
    # Return a real error status so client code can detect the failure
    if result is None:
        raise HTTPException(status_code=422, detail="Could not extract invoice data")
    # FastAPI converts the Pydantic Invoice model to JSON automatically
    return result
