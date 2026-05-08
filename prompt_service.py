from __future__ import annotations

from typing import Iterable


def format_history(history: Iterable[tuple[str, str]]) -> str:
    turns = list(history)
    if not turns:
        return "No previous conversation."

    return "\n".join(
        f"User: {user_msg}\nAssistant: {assistant_msg}"
        for user_msg, assistant_msg in turns
    )


def build_single_prompt(question: str, context: str, history=None) -> str:
    history_text = format_history(history or [])
    return f"""
You are a helpful AI study assistant.
Answer the student's question using only the provided context from the uploaded document.
If the answer is not found in the context, say that clearly.
Explain in a simple and clear way.

Conversation History:
{history_text}

Context:
{context}

Question:
{question}

Answer:
""".strip()


def build_multi_prompt(question: str, combined_context: str, history=None) -> str:
    history_text = format_history(history or [])
    return f"""
You are a helpful AI study assistant.
The student asked a question about multiple uploaded documents.

Use only the provided context from the different sources below.
If the answer is spread across more than one file, combine it clearly.
If the files disagree, mention the difference.
If the answer is not found in the context, say that clearly.
Always mention which source(s) you used.

Conversation History:
{history_text}

Combined Context:
{combined_context}

Question:
{question}

Answer:
""".strip()


def build_detailed_explanation_prompt(question: str, context: str, history=None) -> str:
    history_text = format_history(history or [])
    return f"""
You are a helpful AI study assistant.

The user wants a detailed explanation of the uploaded document, not just a short answer.
Use only the provided context from the uploaded document.
If some parts of the document are not covered enough by the context, say that clearly instead of inventing content.

Your answer must be detailed, structured, and easy to study from.
Organize the explanation using this structure when possible:

1. Main topic of the lecture/document
2. Major sections or ideas covered
3. Detailed explanation of each important point
4. Important terms, definitions, or concepts
5. Simple examples or clarifications when possible
6. Final summary

Important rules:
- Do not give only a short summary.
- Do not answer in one paragraph unless the context is actually very short.
- Prefer headings and bullet points when useful.
- Answer in the same language as the user's question.

Conversation History:
{history_text}

Context:
{context}

Question:
{question}

Answer:
""".strip()
