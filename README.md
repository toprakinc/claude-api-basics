# Claude API Basics

Learning project: building practical AI tools on top of the Claude API in Python, from a terminal chatbot to a tool-using support bot that answers from a company's PDF help center.

## Projects

### 1. StepUp support bot (tool calling + RAG)

A customer support chatbot for a fictional shoe store, **StepUp**. It can:

- look up order status (`get_order_status`)
- create returns, with business rules enforced in code (`create_return_request`)
- answer store policy questions from a PDF help center (`search_docs`)

### 2. Help center RAG with evaluation

Answers questions using only the company's PDF documents and says "I don't know" when the answer isn't there. Search quality is measured with a 15-question test set.

### 3. Invoice extractor (structured output + FastAPI)

Extracts vendor, total, currency and line items from invoice text, validates them with Pydantic and exposes the extractor as an HTTP API.

## Files

| File               | What it does                                                                                                                   |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| `chat.py`          | StepUp support bot. Keeps conversation history, runs a tool loop until Claude writes the final answer.                         |
| `store_tools.py`   | The bot's tools: fake order database, tool definitions and the functions that run them. Loads the help center once at startup. |
| `rag.py`           | RAG pipeline: read PDF, split into sections, embed with Voyage AI, search by meaning, answer with Claude.                      |
| `eval_set.py`      | 15 test questions with the exact phrase each answer must contain.                                                              |
| `evaluate.py`      | Runs the test set and compares keyword search vs semantic search.                                                              |
| `help_center.pdf`  | StepUp help center: shipping, returns, exchanges, sizing, payment, shoe care, contact.                                         |
| `extract.py`       | Invoice extraction with Pydantic validation; processes every `.txt` in `invoices/` and saves `results.csv`.                    |
| `app.py`           | FastAPI service exposing the invoice extractor.                                                                                |
| `main.py`          | Minimal example: one message to Claude, with error handling.                                                                   |
| `support_tools.py` | Minimal tool calling example: one question, one tool call, one answer.                                                         |

## How the RAG pipeline works

1. **Read** the PDF with `pypdf`.
2. **Split** it into one chunk per section, cutting at each heading (`chunk_by_headings`).
3. **Embed** every chunk once with Voyage AI (`voyage-3.5-lite`), turning text into vectors that represent meaning.
4. **Search:** embed the question, score each chunk with a dot product (`similarity`) and take the closest chunks.
5. **Answer:** send only those chunks to Claude with one rule: answer from the documents, or say "I don't know".

## Measuring search quality

`evaluate.py` asks 15 questions and checks whether the top chunk (k=1) contains the expected answer. Half of the questions use different words than the document (for example _"Can I send back sneakers I already wore?"_ vs _"Returns are accepted... Shoes must be unworn."_).

| Chunking                | Search                 | Score     |
| ----------------------- | ---------------------- | --------- |
| 80-word chunks          | Keyword (shared words) | 8/15      |
| 80-word chunks          | Semantic (embeddings)  | 12/15     |
| Sections by heading     | Keyword                | 9/15      |
| **Sections by heading** | **Semantic**           | **14/15** |

What this showed:

- Keyword search fails when customers use different words than the document.
- Fixed-size chunks mixed several topics in one chunk, which blurred their embeddings. Splitting by headings (one topic per chunk) fixed most of the remaining misses.

## Safety: rules in the prompt and in the code

- **Prompt:** the bot must summarize a return and get the customer's explicit "yes" before creating it, and must answer policy questions only from `search_docs`.
- **Code:** `create_return_request` checks the business rules itself (order exists, is delivered, is within 30 days, no duplicate). Even if the model is talked into calling the tool, invalid returns are rejected.

## Example

```
You: Can I pay with Klarna?
  [tool] search_docs({'query': 'Can I pay with Klarna?'})
Claude: Yes, you can pay with Klarna. It's available as 4 interest-free installments on orders over $100.

You: Where is my order 1001?
  [tool] get_order_status({'order_id': '1001'})
Claude: Your order 1001 has shipped with UPS.

You: Can I send back sneakers I already wore?
  [tool] search_docs({'query': 'Can I return shoes that I already wore?'})
Claude: No, I'm afraid we can't accept returns of shoes that have been worn...
```

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```
ANTHROPIC_API_KEY=your_key
VOYAGE_API_KEY=your_key
```

Run:

```bash
python chat.py        # support bot
python evaluate.py    # search quality test
```

Note: Voyage accounts without a payment method are limited to 3 requests per minute. `evaluate.py` embeds all questions in a single request to stay under the limit.

## Limitations

- The store, orders and help center are fictional.
- Section headings are listed by hand; a real project would detect them from the PDF's structure.
- Vectors are kept in memory, which is fine for one small document but not for thousands.
- The test set has 15 questions, enough to compare approaches but not to claim a precise accuracy.
