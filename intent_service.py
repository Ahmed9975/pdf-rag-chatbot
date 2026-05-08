from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from manager import MultiPDFManager

Mode = Literal["Auto", "General Chat", "Active PDF", "All PDFs"]
ResolvedMode = Literal["General Chat", "Active PDF", "All PDFs"]

_FILE_COMMAND_PATTERNS = [
    r"use file\s+(\d+)",
    r"select file\s+(\d+)",
    r"open file\s+(\d+)",
    r"استخدم الملف\s+(\d+)",
    r"اختار الملف\s+(\d+)",
    r"افتح الملف\s+(\d+)",
]

LIST_KEYWORDS = {
    "list files",
    "show files",
    "current files",
    "uploaded files",
    "اعرض الملفات",
    "عرض الملفات",
}

ALL_FILES_KEYWORDS = {
    "all files",
    "all pdfs",
    "compare all files",
    "compare files",
    "compare documents",
    "كل الملفات",
    "كل الفايلات",
    "قارن الملفات",
    "المستندات كلها",
}

DETAILED_KEYWORDS = {
    "in detail",
    "detailed explanation",
    "full explanation",
    "explain the whole lecture",
    "explain the whole document",
    "summarize the whole document",
    "walk me through",
    "step by step",
    "comprehensive explanation",
    "بالتفصيل",
    "بالتفاصيل",
    "اشرح المحاضرة",
    "اشرح الملف",
    "اشرحلي المحاضرة",
    "اشرحلي الملف",
    "اشرح اللي موجود",
    "اشرح الموجود",
    "امشي معايا في المحاضرة",
    "اشرح نقطة نقطة",
    "لخص بالتفصيل",
    "شرح كامل",
    "لخص المحاضرة كاملة",
    "لخص الملف كامل",
    "الملف كله",
    "المحاضرة كلها",
}

DOCUMENT_HINTS = {
    "pdf",
    "document",
    "lecture",
    "chapter",
    "from the file",
    "from the pdf",
    "explain the file",
    "summarize the file",
    "the uploaded file",
    "الملف",
    "المحاضرة",
    "المستند",
    "الpdf",
    "من الملف",
    "في الملف",
    "في المحاضرة",
    "لخص الملف",
}


@dataclass
class ParsedIntent:
    mode: ResolvedMode | None = None
    wants_file_list: bool = False
    wants_detailed: bool = False
    requested_file_number: int | None = None


def _contains_any(text: str, keywords: set[str]) -> bool:
    lowered = text.lower().strip()
    return any(keyword in lowered for keyword in keywords)


def extract_file_number(text: str) -> int | None:
    for pattern in _FILE_COMMAND_PATTERNS:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def wants_file_list(text: str) -> bool:
    return _contains_any(text, LIST_KEYWORDS)


def wants_all_files(text: str, manager: MultiPDFManager) -> bool:
    return len(manager.list_pdfs()) > 1 and _contains_any(text, ALL_FILES_KEYWORDS)


def wants_detailed_document_explanation(text: str) -> bool:
    return _contains_any(text, DETAILED_KEYWORDS)


def wants_document_mode(text: str, manager: MultiPDFManager) -> bool:
    if not manager.has_pdfs():
        return False
    return _contains_any(text, DOCUMENT_HINTS)


def parse_intent(text: str, manager: MultiPDFManager, mode: Mode, detailed: bool) -> ParsedIntent:
    parsed = ParsedIntent(
        wants_file_list=wants_file_list(text),
        wants_detailed=detailed or wants_detailed_document_explanation(text),
        requested_file_number=extract_file_number(text),
    )

    if mode != "Auto":
        parsed.mode = mode
        return parsed

    if not manager.has_pdfs():
        parsed.mode = "General Chat"
    elif wants_all_files(text, manager):
        parsed.mode = "All PDFs"
    elif wants_document_mode(text, manager):
        parsed.mode = "Active PDF"
    else:
        parsed.mode = "General Chat"

    return parsed
