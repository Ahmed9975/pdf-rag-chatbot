from __future__ import annotations

from config import WELCOME_MESSAGE
from document_service import answer_all_pdfs, answer_general, answer_pdf, upload_pdfs
from intent_service import Mode, parse_intent
from manager import MultiPDFManager


def create_manager() -> MultiPDFManager:
    return MultiPDFManager(verbose=False)


def format_files_list(manager: MultiPDFManager) -> str:
    files = manager.list_pdfs()
    if not files:
        return "### Uploaded files\nNo uploaded files yet."

    active_file = manager.get_active_pdf()
    lines = ["### Uploaded files"]
    for index, file_id in enumerate(files, start=1):
        marker = " ← active" if file_id == active_file else ""
        lines.append(f"{index}. `{file_id}`{marker}")
    return "\n".join(lines)


def apply_file_selection(manager: MultiPDFManager, selection: str | None) -> str:
    if not selection:
        manager.ensure_active_pdf()
        return manager.get_active_pdf() or ""

    files = manager.list_pdfs()
    if selection in files:
        manager.set_active_pdf(selection)
        return selection

    if selection.isdigit():
        index = int(selection) - 1
        if 0 <= index < len(files):
            selected_file = files[index]
            manager.set_active_pdf(selected_file)
            return selected_file

    raise ValueError("Invalid file selection.")


def route_message(
    manager: MultiPDFManager | None,
    text: str,
    mode: Mode = "Auto",
    detailed: bool = False,
):
    manager = manager or create_manager()
    text = (text or "").strip()
    if not text:
        return manager, "Please enter a message."

    parsed = parse_intent(text=text, manager=manager, mode=mode, detailed=detailed)

    if parsed.wants_file_list:
        return manager, format_files_list(manager)

    if parsed.requested_file_number is not None:
        files = manager.list_pdfs()
        if not files:
            return manager, "No uploaded files."

        index = parsed.requested_file_number - 1
        if index < 0 or index >= len(files):
            return manager, "Invalid file number."

        selected_file = files[index]
        manager.set_active_pdf(selected_file)
        return manager, f"Active file set to:\n`{selected_file}`"

    if parsed.mode == "General Chat":
        return manager, answer_general(text)

    if parsed.mode == "All PDFs":
        if not manager.has_pdfs():
            return manager, "Please upload PDF files first."
        return manager, answer_all_pdfs(manager, text, detailed=parsed.wants_detailed)

    manager.ensure_active_pdf()
    if not manager.get_active_pdf():
        return manager, "Please upload a PDF file first."
    return manager, answer_pdf(manager, text, detailed=parsed.wants_detailed)


__all__ = [
    "WELCOME_MESSAGE",
    "apply_file_selection",
    "create_manager",
    "format_files_list",
    "route_message",
    "upload_pdfs",
]
