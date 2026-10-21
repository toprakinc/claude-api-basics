# Claude API Basics

A minimal Python script that sends a message to the Claude API and prints the response.

This is the first step of my AI engineering roadmap, where I'm building toward real-world AI automation projects (customer support bots, document processing, and email automation).

## Tech Stack

- Python 3
- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)
- python-dotenv

## Setup

1. Clone the repository:

```bash
   git clone https://github.com/toprakinc/claude-api-basics.git
   cd claude-api-basics
```

2. Create and activate a virtual environment:

```bash
   python3 -m venv .venv
   source .venv/bin/activate
```

3. Install dependencies:

```bash
   pip install -r requirements.txt
```

4. Create a `.env` file and add your API key:

```
   ANTHROPIC_API_KEY=your-api-key-here
```

## Usage

```bash
python main.py
```

## Next Steps

- [ ] Add error handling
- [ ] Build an interactive terminal chatbot
