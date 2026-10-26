# Claude API Basics

Learning project: building practical tools on top of the Claude API in Python, from a terminal chatbot to an invoice extraction API.

## Files

- `main.py` – Sends a single message to Claude and prints the reply. Handles connection and API errors.
- `chat.py` – Terminal chatbot with conversation memory. Acts as a customer support assistant for a fictional shoe store, **StepUp**, using a system prompt that contains the store's policies.
- `extract.py` – Extracts structured data (vendor, total, currency, line items) from invoice text and validates it with Pydantic. Processes every `.txt` file in `invoices/` and saves a summary to `results.csv`.
- `app.py` – FastAPI web service that exposes the invoice extractor as an HTTP API.

## How `chat.py` works

- Keeps the conversation in a `history` list (alternating `user` / `assistant` messages) and sends it with every request, so the bot remembers earlier messages.
- Uses a `SYSTEM_PROMPT` to define the bot's role and store policies.
- If a request fails, the last user message is removed from `history` so the conversation can continue cleanly.

## How `extract.py` works

- Asks Claude to return the invoice data as JSON only.
- Validates the reply with Pydantic models (`Invoice`, `LineItem`), so missing fields or wrong types are caught instead of silently passing through.
- Checks that the line items add up to the stated total and marks each invoice as `OK`, `WARNING` (totals don't match) or `FAILED` (could not extract).
- Can be imported by other modules: the batch processing only runs when the file is executed directly.

## Setup

```bash
git clone https://github.com/toprakinc/claude-api-basics.git
cd claude-api-basics
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project folder:

```
ANTHROPIC_API_KEY=your_api_key_here
```

## Run

```bash
python main.py      # single message
python chat.py      # chatbot (type "quit" to exit)
python extract.py   # process all invoices in invoices/
```

## Invoice Extraction API (FastAPI)

The invoice extractor is also available as a web API, so other applications can send invoice text and receive structured JSON.

### Run the server

```bash
uvicorn app:app --reload
```

Interactive docs: http://127.0.0.1:8000/docs

### Endpoints

| Method | Path       | Description                                |
| ------ | ---------- | ------------------------------------------ |
| GET    | `/`        | Welcome message                            |
| GET    | `/health`  | Health check, returns server status        |
| POST   | `/extract` | Extracts structured data from invoice text |

### Example request

```bash
curl -X POST http://127.0.0.1:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "Bright Supplies Inc.\nItem: Printer paper (box) - qty 5 @ $12.00\nItem: Ink cartridge - qty 2 @ $35.50\nAmount due: $131.00"}'
```

### Example response (200)

```json
{
  "vendor": "Bright Supplies Inc.",
  "total": 131.0,
  "currency": "USD",
  "items": [
    { "description": "Printer paper (box)", "quantity": 5, "unit_price": 12.0 },
    { "description": "Ink cartridge", "quantity": 2, "unit_price": 35.5 }
  ]
}
```

### Errors

- `422` with `"Could not extract invoice data"` when the text can't be parsed into a valid invoice.
- `422` with validation details when the request body is not valid JSON or is missing `text`.
