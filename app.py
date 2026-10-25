from fastapi import FastAPI  # import the FastAPI class

app = FastAPI()  # create the web app


@app.get("/")  # when someone visits the main address...
def home():  # ...run this function
    return {"message": "Invoice API is running"}  # send back JSON


@app.get("/health")
def health():
    return {"status": "ok"}
