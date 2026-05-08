from __future__ import annotations

from config import (
    DETAILED_OVERVIEW_CHUNKS,
    DETAILED_RELEVANT_K,
    MULTI_FILE_DETAILED_K,
    MULTI_FILE_K,
)
from llm import get_response
from manager import MultiPDFManager
from prompt_service import (
    build_detailed_explanation_prompt,
    build_multi_prompt,
    build_single_prompt,
)


def answer_general(question: str) -> str:
    return get_response(question)


def select_spread_chunks(chunks, n: int = DETAILED_OVERVIEW_CHUNKS):
    if not chunks:
        return []
    if len(chunks) <= n:
        return chunks

    selected = []
    used_indices = set()
    step = (len(chunks) - 1) / (n - 1)
    for i in range(n):
        index = round(i * step)
        if index not in used_indices:
            selected.append(chunks[index])
            used_indices.add(index)
    return selected


def explain_document_in_detail(
    manager: MultiPDFManager,
    question: str,
    file_id: str | None = None,
    relevant_k: int = DETAILED_RELEVANT_K,
    overview_chunks: int = DETAILED_OVERVIEW_CHUNKS,
) -> str:
    pipeline = manager.get_pipeline(file_id)
    pipeline.ensure_ready()

    prefixed_question = (
        "Instruct: Given a question, retrieve relevant passages\n"
        f"Query: {question}"
    )
    matched_docs = pipeline.vector_store.similarity_search_with_score(
        prefixed_question,
        k=relevant_k,
    )

    relevant_docs = [doc for doc, _ in matched_docs]
    spread_docs = select_spread_chunks(pipeline.chunks, n=overview_chunks)

    collected_docs = []
    seen_texts = set()

    def add_doc(doc, source_label: str) -> None:
        text = doc.page_content.strip()
        if text and text not in seen_texts:
            collected_docs.append(
                {
                    "source": source_label,
                    "page": doc.metadata.get("page", "N/A"),
                    "text": text,
                }
            )
            seen_texts.add(text)

    for doc in relevant_docs:
        add_doc(doc, "Most Relevant")
    for doc in spread_docs:
        add_doc(doc, "Document Coverage")

    if not collected_docs:
        return "No useful context found in the document."

    combined_context = "\n\n".join(
        f"[{item['source']}] Page: {item['page']}\n{item['text']}"
        for item in collected_docs
    )
    prompt = build_detailed_explanation_prompt(
        question=question,
        context=combined_context,
        history=pipeline.history,
    )
    answer = get_response(prompt)
    pipeline.add_history_turn(question, answer)
    return answer


def answer_pdf(
    manager: MultiPDFManager,
    question: str,
    file_id: str | None = None,
    detailed: bool = False,
) -> str:
    if detailed:
        return explain_document_in_detail(manager, question, file_id=file_id)

    pipeline = manager.get_pipeline(file_id)
    context = pipeline.retrieve_context(question)
    prompt = build_single_prompt(question, context, pipeline.history)
    answer = get_response(prompt)
    pipeline.add_history_turn(question, answer)
    return answer


def build_multi_context(
    manager: MultiPDFManager,
    file_ids: list[str],
    question: str,
    k_per_pdf: int,
) -> str:
    if not file_ids:
        raise ValueError("No PDF files were provided.")

    context_parts = []
    for file_id in file_ids:
        pipeline = manager.get_pipeline(file_id)
        context = pipeline.retrieve_context(question, k=k_per_pdf)
        context_parts.append(f"[Source: {file_id}]\n{context}")
    return "\n\n".join(context_parts)


def answer_multiple_pdfs(
    manager: MultiPDFManager,
    file_ids: list[str],
    question: str,
    detailed: bool = False,
) -> str:
    k_per_pdf = MULTI_FILE_DETAILED_K if detailed else MULTI_FILE_K
    combined_context = build_multi_context(manager, file_ids, question, k_per_pdf=k_per_pdf)

    merged_history = []
    for file_id in file_ids:
        pipeline = manager.get_pipeline(file_id)
        merged_history.extend(pipeline.history[-2:])

    prompt = build_multi_prompt(question, combined_context, history=merged_history)
    answer = get_response(prompt)

    for file_id in file_ids:
        manager.get_pipeline(file_id).add_history_turn(question, answer)
    return answer


def answer_all_pdfs(manager: MultiPDFManager, question: str, detailed: bool = False) -> str:
    file_ids = manager.list_pdfs()
    if not file_ids:
        return "Please upload PDF files first."
    return answer_multiple_pdfs(manager, file_ids, question, detailed=detailed)


def upload_pdfs(file_paths, manager: MultiPDFManager | None):
    manager = manager or MultiPDFManager(verbose=False)
    if not file_paths:
        return manager, "No files uploaded."

    if isinstance(file_paths, str):
        file_paths = [file_paths]

    prepared = []
    for index, file_path in enumerate(file_paths):
        file_id = manager.add_pdf(file_path, set_active=(index == len(file_paths) - 1))
        pipeline = manager.get_pipeline(file_id)
        pipeline.build_vector_store()
        prepared.append(file_id)

    active_file = manager.get_active_pdf() or "None"
    uploaded_list = "\n".join(f"- `{file_id}`" for file_id in prepared)
    status = (
        f"Prepared {len(prepared)} file(s) successfully.\n\n"
        f"{uploaded_list}\n\n"
        f"Active file: `{active_file}`"
    )
    return manager, status
