# Claude API Basics

Learning project: building practical tools on top of the Claude API in Python, from a terminal chatbot to a tool-using support bot and an invoice extraction API.

## Files

- `main.py` – Sends a single message to Claude and prints the reply. Handles connection and API errors.
- `chat.py` – Customer support chatbot for a fictional shoe store, **StepUp**. Remembers the conversation and uses tools to look up orders and create returns.
- `store_tools.py` – The store's tools: a fake order database, tool definitions for Claude, and the functions that run them.
- `support_tools.py` – Minimal tool calling example: one question, one tool call, one answer.
- `extract.py` – Extracts structured data (vendor, total, currency, line items) from invoice text and validates it with Pydantic. Processes every `.txt` file in `invoices/` and saves a summary to `results.csv`.
- `app.py` – FastAPI web service that exposes the invoice extractor as an HTTP API.

## How `chat.py` works

- Keeps the conversation in a `history` list and sends it with every request, so the bot remembers earlier messages.
- Uses a `SYSTEM_PROMPT` to define the bot's role, store policies and how to handle returns.
- Gives Claude two tools:
  - `get_order_status` – looks up an order's status, carrier and delivery date.
  - `create_return_request` – creates a return for a delivered order.
- Runs a tool loop: while Claude asks for tools, the code runs them and sends the results back, until Claude writes the final answer.
- If a request fails, everything added during that turn is removed from `history`, so the conversation stays valid.

### Safety: rules in the prompt and in the code

- **Prompt:** the bot must summarize a return and get the customer's explicit "yes" before creating it.
- **Code:** `create_return_request` checks the business rules itself (order exists, is delivered, is within 30 days, no duplicate return). Even if the model is persuaded to call the tool, invalid returns are rejected.

### Example

```
You: I want to return order 1003, the size is wrong
  [tool] get_order_status({'order_id': '1003'})
Claude: Order 1003 was delivered on October 20, 2026, so it's eligible for a return.
        Order: 1003, Reason: Wrong size. Would you like me to submit this return?
You: yes
  [tool] create_return_request({'order_id': '1003', 'reason': 'Wrong size'})
Claude: Your return for order 1003 is created. Your return ID is R-1003.
```

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
python main.py            # single message
python chat.py            # support chatbot with tools (type "quit" to exit)
python support_tools.py   # minimal tool calling example
python extract.py         # process all invoices in invoices/
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
