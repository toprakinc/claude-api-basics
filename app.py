from fastapi import FastAPI  # import the FastAPI class
from pydantic import BaseModel

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
    return {"characters": len(data.text)}
