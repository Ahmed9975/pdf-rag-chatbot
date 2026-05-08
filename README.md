# pdf-rag-chatbot
# PDF RAG Chatbot - AI Study Assistant

A practical Generative AI and Retrieval-Augmented Generation (RAG) project that allows users to upload PDF files, ask questions about their content, and receive context-aware answers based on the most relevant retrieved passages.

The project is designed as an AI study assistant that can work with one or more PDF documents and answer questions in a simple, structured, and useful way.

---

## Features

- Upload one or multiple PDF files
- Ask questions about uploaded documents
- Retrieve the most relevant chunks from PDFs using semantic search
- Generate answers using a local LLM through Ollama
- Support active PDF selection
- Support answering across all uploaded PDFs
- Detailed explanation mode for deeper study-style answers
- Simple Gradio user interface
- Local FAISS vector index storage
- Supports multilingual embeddings

---

## Tech Stack

- Python
- Gradio
- LangChain
- FAISS
- Hugging Face Embeddings
- Ollama
- PyPDFLoader
- RecursiveCharacterTextSplitter

---

## Models Used

### LLM

The project uses a local Ollama model:

```bash
qwen3:8b
```

### Embedding Model

```bash
intfloat/multilingual-e5-large-instruct
```

This embedding model is used to convert PDF chunks into vector representations for semantic search.

---

## Project Structure

```text
.
├── app.py
├── config.py
├── document_service.py
├── intent_service.py
├── llm.py
├── main.py
├── manager.py
├── Pipeline.py
├── prompt_service.py
├── requirements.txt
└── README.md
```

---

## File Overview

| File | Description |
|---|---|
| `app.py` | Main Gradio interface |
| `config.py` | Project configuration and model settings |
| `Pipeline.py` | PDF loading, chunking, embeddings, and FAISS vector store |
| `manager.py` | Manages multiple uploaded PDFs |
| `document_service.py` | Handles PDF-based question answering |
| `intent_service.py` | Detects user intent and routing mode |
| `llm.py` | Handles communication with Ollama |
| `prompt_service.py` | Builds prompts for single PDF, multiple PDFs, and detailed explanation |
| `main.py` | Main routing logic between chat and document modes |

---

## How It Works

1. The user uploads one or more PDF files.
2. The system loads the PDF content using `PyPDFLoader`.
3. The text is split into smaller chunks using `RecursiveCharacterTextSplitter`.
4. Each chunk is converted into embeddings using a Hugging Face embedding model.
5. FAISS stores the vector embeddings locally.
6. When the user asks a question, the system retrieves the most relevant chunks.
7. The retrieved context is passed to a local LLM through Ollama.
8. The model generates an answer based only on the retrieved document context.

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Ahmed9975/pdf-rag-chatbot.git
cd pdf-rag-chatbot
```

---

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the virtual environment:

#### Windows

```bash
venv\Scripts\activate
```

#### macOS / Linux

```bash
source venv/bin/activate
```

---

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

---

### 4. Install and Run Ollama

Download and install Ollama from:

```text
https://ollama.com
```

Then pull the required model:

```bash
ollama pull qwen3:8b
```

Make sure Ollama is running before starting the project.

---

## Run the App

```bash
python app.py
```

After running the command, Gradio will provide a local URL. Open it in your browser.

Example:

```text
http://127.0.0.1:7860
```

---

## Usage

1. Open the app in your browser.
2. Upload one or more PDF files.
3. Select the active PDF if needed.
4. Ask a question about the document.
5. Choose between:
   - General Chat
   - Active PDF
   - All PDFs
   - Auto Mode
6. Enable Detailed Mode for deeper explanations.

---

## Example Questions

```text
Summarize the active PDF
```

```text
Explain this lecture step by step
```

```text
Compare all uploaded files
```

```text
What are the main ideas in this document?
```

```text
List uploaded files
```

---

## Notes

- FAISS indexes are generated locally and are not included in the repository.
- Uploaded PDFs are not included in the repository.
- The project runs locally using Ollama, so no external LLM API key is required.
- The first run may take some time because the embedding model may need to be downloaded.

---

## Security Notes

The following files and folders should not be uploaded to GitHub:

```text
.env
faiss_indexes/
*.pdf
__pycache__/
*.pyc
```

These are excluded using `.gitignore`.

---

## Learning Outcomes

This project helped me understand and apply the core components of a real RAG pipeline, including:

- Document loading
- Text chunking
- Embedding generation
- Vector search
- Context retrieval
- Prompt construction
- Local LLM response generation
- Building an interactive AI application

---

## Author

Ahmed Abdelfattah

Final-year Computer Science student focused on AI, Machine Learning, NLP, and Generative AI.
