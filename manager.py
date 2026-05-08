from __future__ import annotations

import hashlib
from pathlib import Path

from Pipeline import Pipeline


class MultiPDFManager:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.pipelines: dict[str, Pipeline] = {}
        self.active_file: str | None = None

    @staticmethod
    def make_file_key(file_path: str) -> str:
        file_name = Path(file_path).name
        file_key = hashlib.md5(str(Path(file_path).resolve()).encode()).hexdigest()[:8]
        return f"{file_name}_{file_key}"

    def add_pdf(self, file_path: str, set_active: bool = True) -> str:
        file_id = self.make_file_key(file_path)
        if file_id not in self.pipelines:
            self.pipelines[file_id] = Pipeline(file_path=file_path, verbose=self.verbose)
            if self.verbose:
                print(f"Added PDF: {file_id}")

        if set_active:
            self.active_file = file_id
        return file_id

    def list_pdfs(self) -> list[str]:
        return list(self.pipelines.keys())

    def has_pdfs(self) -> bool:
        return bool(self.pipelines)

    def set_active_pdf(self, file_id: str) -> None:
        if file_id not in self.pipelines:
            raise ValueError(f"PDF '{file_id}' not found.")
        self.active_file = file_id

    def get_active_pdf(self) -> str | None:
        return self.active_file

    def get_pipeline(self, file_id: str | None = None) -> Pipeline:
        target_id = file_id or self.active_file
        if target_id is None:
            raise ValueError("No active PDF is selected.")
        if target_id not in self.pipelines:
            raise ValueError(f"PDF '{target_id}' not found.")
        return self.pipelines[target_id]

    def ensure_active_pdf(self) -> str | None:
        if self.active_file is None and self.pipelines:
            self.active_file = next(iter(self.pipelines))
        return self.active_file

    def remove_pdf(self, file_id: str) -> None:
        if file_id not in self.pipelines:
            raise ValueError(f"PDF '{file_id}' not found.")
        del self.pipelines[file_id]
        if self.active_file == file_id:
            self.active_file = next(iter(self.pipelines), None)

    def clear_all(self) -> None:
        self.pipelines.clear()
        self.active_file = None
