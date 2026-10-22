# Claude API Basics

Learning project: calling the Claude API from Python and building a simple terminal chatbot.

## Files

- `main.py` – Sends a single message to Claude and prints the reply. Handles connection and API errors.
- `chat.py` – Terminal chatbot with conversation memory. Acts as a customer support assistant for a fictional shoe store, **StepUp**, using a system prompt that contains the store's policies.

## How `chat.py` works

- Keeps the conversation in a `history` list (alternating `user` / `assistant` messages) and sends it with every request, so the bot remembers earlier messages.
- Uses a `SYSTEM_PROMPT` to define the bot's role and store policies.
- If a request fails, the last user message is removed from `history` so the conversation can continue cleanly.

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
python main.py   # single message
python chat.py   # chatbot (type "quit" to exit)
```
