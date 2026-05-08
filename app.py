from __future__ import annotations

import html

import gradio as gr
import config

from main import create_manager, route_message, upload_pdfs


APP_TITLE = getattr(config, "APP_TITLE", "AI Study Assistant")
APP_SUBTITLE = "Ask about your PDFs, skills, qualifications, and requirements."
INPUT_PLACEHOLDER = "Ask anything..."
EMPTY_QUESTION_TEXT = "Your question will appear here."
EMPTY_ANSWER_TEXT = "The answer will appear here."


CUSTOM_CSS = """
html, body {
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
    min-height: 100% !important;
    background: #07111f !important;
    color: #f8fafc !important;
    overflow-x: hidden !important;
    font-family: Arial, sans-serif !important;
}

body > gradio-app,
.gradio-container {
    width: 100% !important;
    min-height: 100vh !important;
    margin: 0 !important;
    padding: 0 !important;
    background:
        radial-gradient(circle at top left, rgba(59, 130, 246, 0.10), transparent 24%),
        radial-gradient(circle at top right, rgba(37, 99, 235, 0.12), transparent 24%),
        linear-gradient(180deg, #07111f 0%, #0b1220 100%) !important;
}

footer {
    display: none !important;
}

#page {
    width: 100% !important;
    max-width: 1260px !important;
    margin: 0 auto !important;
    padding: 28px 24px 40px 24px !important;
    box-sizing: border-box !important;
}

#hero {
    margin-bottom: 18px !important;
}

#hero h1 {
    margin: 0 !important;
    font-size: 42px !important;
    line-height: 1.2 !important;
    font-weight: 800 !important;
    color: #f8fafc !important;
}

#hero p {
    margin: 10px 0 0 0 !important;
    font-size: 22px !important;
    line-height: 1.6 !important;
    color: #dbe7ff !important;
}

#controls-box {
    margin-bottom: 26px !important;
    border-radius: 22px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    background: rgba(255,255,255,0.04) !important;
    overflow: hidden !important;
}

#controls-box *,
#controls-box label,
#controls-box input,
#controls-box select,
#controls-box button,
#controls-box span,
#controls-box textarea {
    font-size: 18px !important;
}

#section-label {
    margin: 6px 0 12px 0 !important;
    font-size: 30px !important;
    font-weight: 700 !important;
    color: #f8fafc !important;
}

#ask-row {
    align-items: stretch !important;
    gap: 18px !important;
    margin-bottom: 26px !important;
}

#question-input textarea,
#question-input input {
    min-height: 72px !important;
    font-size: 26px !important;
    line-height: 1.5 !important;
    padding: 18px 22px !important;
    border-radius: 26px !important;
    background: rgba(0, 0, 0, 0.58) !important;
    border: 2px solid rgba(255,255,255,0.10) !important;
    color: #ffffff !important;
}

#question-input textarea::placeholder,
#question-input input::placeholder {
    color: #94a3b8 !important;
    opacity: 1 !important;
}

#ask-btn {
    min-height: 72px !important;
    border-radius: 24px !important;
    font-size: 26px !important;
    font-weight: 700 !important;
}

#ask-btn button {
    min-height: 72px !important;
    border-radius: 24px !important;
    font-size: 26px !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
    border: none !important;
    color: white !important;
}

.qa-card {
    border-radius: 28px !important;
    padding: 24px 28px !important;
    margin-bottom: 24px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    box-shadow: 0 20px 40px rgba(0,0,0,0.18) !important;
}

.question-card {
    background: linear-gradient(180deg, rgba(24, 55, 112, 0.92), rgba(20, 44, 92, 0.92)) !important;
}

.answer-card {
    background: rgba(2, 6, 23, 0.92) !important;
}

.eyebrow {
    font-size: 18px !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    margin-bottom: 18px !important;
}

.question-eyebrow {
    color: #60a5fa !important;
}

.answer-eyebrow {
    color: #4ade80 !important;
}

#question-view .question-text {
    font-size: 30px !important;
    line-height: 1.6 !important;
    color: #f8fafc !important;
    font-weight: 500 !important;
}

#question-view .placeholder {
    color: #cbd5e1 !important;
}

#answer-view {
    font-size: 24px !important;
    line-height: 1.9 !important;
    color: #f8fafc !important;
}

#answer-view p,
#answer-view li,
#answer-view div,
#answer-view span,
#answer-view strong,
#answer-view em,
#answer-view code,
#answer-view h1,
#answer-view h2,
#answer-view h3,
#answer-view h4 {
    font-size: inherit !important;
    line-height: inherit !important;
    color: inherit !important;
}

#answer-view ul,
#answer-view ol {
    padding-left: 1.6em !important;
}

button,
textarea,
input,
select {
    border-radius: 16px !important;
}

.compact-file {
    min-height: 78px !important;
}

.status-text {
    color: #dbe7ff !important;
    margin: 10px 0 0 0 !important;
    font-size: 18px !important;
    line-height: 1.6 !important;
}
"""


def _file_dropdown_update(manager):
    files = manager.list_pdfs()
    active = manager.get_active_pdf() if files else None
    return gr.update(choices=files, value=active)


def _render_question(text: str) -> str:
    if not text:
        return f"<div class='question-text placeholder'>{EMPTY_QUESTION_TEXT}</div>"
    return f"<div class='question-text'>{html.escape(text)}</div>"


def handle_upload(files, manager):
    manager = manager or create_manager()

    if not files:
        return manager, _file_dropdown_update(manager), "No files uploaded."

    manager, status = upload_pdfs(files, manager)
    return manager, _file_dropdown_update(manager), status


def handle_file_selection(selected_file, manager):
    manager = manager or create_manager()

    if not selected_file:
        return manager, _file_dropdown_update(manager), "No active file selected."

    try:
        manager.set_active_pdf(selected_file)
        return manager, _file_dropdown_update(manager), f"Active file set to `{selected_file}`"
    except Exception as exc:
        return manager, _file_dropdown_update(manager), f"Error: {exc}"


def clear_workspace():
    manager = create_manager()
    return (
        manager,
        gr.update(choices=[], value=None),
        "",
        _render_question(""),
        EMPTY_ANSWER_TEXT,
        "Workspace cleared.",
    )


def ask_question(question, manager, mode, detailed, selected_file):
    manager = manager or create_manager()

    if not question or not question.strip():
        return (
            "",
            manager,
            _file_dropdown_update(manager),
            _render_question(""),
            EMPTY_ANSWER_TEXT,
            "Please enter a question.",
        )

    user_text = question.strip()

    try:
        if selected_file:
            manager.set_active_pdf(selected_file)

        manager, response = route_message(
            manager=manager,
            text=user_text,
            mode=mode,
            detailed=detailed,
        )

        status = "Ready."
        answer = response
    except Exception as exc:
        status = f"Error: {exc}"
        answer = f"Something went wrong: {exc}"

    return (
        "",
        manager,
        _file_dropdown_update(manager),
        _render_question(user_text),
        answer,
        status,
    )


with gr.Blocks(title=APP_TITLE) as demo:
    manager_state = gr.State(create_manager())

    with gr.Column(elem_id="page"):
        gr.HTML(
            f"""
            <div id="hero">
                <h1>{APP_TITLE}</h1>
                <p>{APP_SUBTITLE}</p>
            </div>
            """
        )

        with gr.Accordion("PDF Controls", open=False, elem_id="controls-box"):
            with gr.Row():
                upload_box = gr.File(
                    label="Upload PDFs",
                    file_count="multiple",
                    file_types=[".pdf"],
                    type="filepath",
                    elem_classes=["compact-file"],
                    scale=4,
                )
                upload_btn = gr.Button("Upload", variant="primary", scale=1)

                file_selector = gr.Dropdown(
                    label="Active PDF",
                    choices=[],
                    value=None,
                    interactive=True,
                    scale=2,
                )

                mode_box = gr.Dropdown(
                    choices=["Auto", "General Chat", "Active PDF", "All PDFs"],
                    value="Auto",
                    label="Mode",
                    scale=2,
                )

                detailed_box = gr.Checkbox(
                    label="Detailed",
                    value=False,
                    scale=1,
                )

                clear_btn = gr.Button("Clear", variant="stop", scale=1)

            status_box = gr.Markdown("Ready.", elem_classes=["status-text"])

        gr.HTML("<div id='section-label'>Your question</div>")

        with gr.Row(elem_id="ask-row"):
            msg = gr.Textbox(
                label="",
                placeholder=INPUT_PLACEHOLDER,
                lines=1,
                scale=8,
                elem_id="question-input",
            )
            ask_btn = gr.Button("Ask", variant="primary", scale=1, elem_id="ask-btn")

        with gr.Column(elem_classes=["qa-card", "question-card"]):
            gr.HTML("<div class='eyebrow question-eyebrow'>YOUR QUESTION</div>")
            question_view = gr.HTML(_render_question(""), elem_id="question-view")

        with gr.Column(elem_classes=["qa-card", "answer-card"]):
            gr.HTML("<div class='eyebrow answer-eyebrow'>ANSWER</div>")
            answer_view = gr.Markdown(EMPTY_ANSWER_TEXT, elem_id="answer-view")

    upload_btn.click(
        fn=handle_upload,
        inputs=[upload_box, manager_state],
        outputs=[manager_state, file_selector, status_box],
    )

    file_selector.change(
        fn=handle_file_selection,
        inputs=[file_selector, manager_state],
        outputs=[manager_state, file_selector, status_box],
    )

    clear_btn.click(
        fn=clear_workspace,
        inputs=[],
        outputs=[manager_state, file_selector, msg, question_view, answer_view, status_box],
    )

    msg.submit(
        fn=ask_question,
        inputs=[msg, manager_state, mode_box, detailed_box, file_selector],
        outputs=[msg, manager_state, file_selector, question_view, answer_view, status_box],
    )

    ask_btn.click(
        fn=ask_question,
        inputs=[msg, manager_state, mode_box, detailed_box, file_selector],
        outputs=[msg, manager_state, file_selector, question_view, answer_view, status_box],
    )

if __name__ == "__main__":
    demo.queue().launch(css=CUSTOM_CSS)