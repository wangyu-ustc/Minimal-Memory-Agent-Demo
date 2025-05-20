Minimal Memory Agent Demo
===========================================

This repo demonstrates a tiny two‑memory agent that talks to **gpt‑4.1‑mini** (replace with any OpenAI model)
and lets the model call four memory‑editing functions (`new_memory_insert`, `memory_update`,
`memory_consolidate`, `memory_delete`).  All memories live in Python lists, so you can run everything
locally without a database.

Quick start
-----------
```bash
python -m venv venv && source venv/bin/activate  # optional
pip install -r requirements.txt
cp .env.example .env                             # add your OPENAI_API_KEY inside
python main.py
```
Type messages; the agent streams replies and updates its memories when the model calls the functions.

Files
-----
* **memory.py** – simple in‑RAM memory store and helper ops
* **functions.py** – Python implementations of the 4 callable tools
* **agent.py** – wraps OpenAI chat loop and routes function calls → Python functions
* **main.py** – CLI loop
* **requirements.txt** – dependencies (`openai>=1.13.3`, `python-dotenv`)