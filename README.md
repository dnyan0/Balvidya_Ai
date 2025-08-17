# 📚 Balvidya – Subject-based Q&A System
Balvidya is an AI-powered educational assistant that helps students (Classes 5th–10th) ask subject-specific questions and receive concise, accurate answers. It uses a Retrieval-Augmented Generation (RAG) pipeline powered by Google Gemini models and integrates with Streamlit for an interactive chat interface.

## 🚀 Features
- **Class & Subject Selection** – Supports multiple classes (5th–10th) and their subjects (Mathematics, Science, English, Physics, Chemistry, Biology, etc.).
- **RAG Pipeline** – Uses FAISS vector stores for retrieving subject-relevant content from .docx study materials.
- **Document Parsing** – Reads and splits class-specific documents into chunks for embedding.
- **Embeddings & LLM** – Uses Google Generative AI embeddings (`models/embedding-001`) and Gemini chat model (`models/gemini-1.5-flash`).
- **Streamlit Chat UI** – User-friendly chat interface with session-based history per (class, subject).
- **Context-Aware Answers** – Priority is given to study material context, with limited fallback knowledge (basic math, grammar, general science).
- **Knowledge Base Management** – Auto-creates or loads FAISS vector stores on first use.

## 🧩 Project Workflow
1.  User selects class & subject from Streamlit sidebar.
2.  System loads corresponding `.docx` file from `documents/{class}/{subject}.docx`.
3.  `rag.py` processes the document:
    - Reads DOCX via `python-docx`
    - Splits into chunks (500 tokens, 50 overlap)
    - Creates embeddings using Google Generative AI (`models/embedding-001`)
    - Builds a FAISS vector store and saves it locally
4.  User asks a question in chat input.
5.  Retrieval pipeline fetches relevant chunks from FAISS.
6.  Gemini Chat model (`gemini-1.5-flash`) generates an answer based on retrieved context.
7.  Answer is displayed in the Streamlit chat interface.

## 📂 Project Structure
```bash 
Balvidya/
├── app.py              # Main Streamlit entry point
├── rag.py              # RAG pipeline (embeddings, vector store, QA)
├── ui.py               # Sidebar & chat interface
├── .env                # API key storage (GOOGLE_API_KEY)
├── requirements.txt    # Python dependencies
├── documents/          # Study material (class/subject DOCX files)
└── vectorstore/        # Auto-generated FAISS indexes
```
## ⚙️ Setup & Installation
1.  **Clone repository**
    ```bash
    git clone [https://github.com/your-username/Balvidya.git](https://github.com/your-username/Balvidya.git)
    cd Balvidya
    ```
2.  **Create virtual environment**
    ```bash
    python -m venv venv
    source venv/bin/activate   # Linux/Mac
    venv\Scripts\activate      # Windows
    ```
3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Setup API key**
    Create a `.env` file in the project root:
    ```
    GOOGLE_API_KEY=your_google_gemini_api_key
    ```
5.  **Run application**
    ```bash
    streamlit run app.py
    ```

## 🧰 Tech Stack
- Python 3.10+
- Streamlit – Web UI framework
- LangChain – RAG orchestration
- FAISS – Vector database for retrieval
- Google Generative AI –
    - Embeddings: `models/embedding-001`
    - Chat model: `models/gemini-1.5-flash`
- `python-docx` – DOCX parsing

## 🎯 Current Capabilities
- Supports subject-based Q&A for 5th–10th classes.
- Can only answer using provided class documents or limited fallback (basic math, grammar, general science).
- Maintains separate chat history per class & subject.
- Builds and caches FAISS vector stores for faster reuse.

## 🚦 Limitations
- No multi-language support (currently English only).
- Requires .docx study material for each subject to answer effectively.
- Limited fallback knowledge – cannot answer beyond allowed scope.
- Local-only storage (no deployment setup included yet).
