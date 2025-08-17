

import os
import pickle
from dotenv import load_dotenv
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import sys
import importlib.util
import nest_asyncio
import shutil

# Apply nest_asyncio to fix event loop issues in Streamlit
nest_asyncio.apply()

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
VECTOR_DIR = "vectorstore"
DOCUMENTS_DIR = "documents"

# Import docx with explicit error handling and module specification
def import_docx():
    try:
        # Try to import the docx module from the installed package
        spec = importlib.util.find_spec("docx")
        if spec is None:
            raise ImportError("The 'python-docx' package is not installed.")
        
        docx_module = importlib.util.module_from_spec(spec)
        sys.modules["docx"] = docx_module
        spec.loader.exec_module(docx_module)
        return docx_module.Document
    except ImportError as e:
        st.error("""
        Error importing python-docx library. Please ensure:
        1. You have installed the correct package: `pip install python-docx`
        2. There are no conflicting files named 'docx.py' in your project
        3. Your environment is properly set up
        """)
        st.error(f"Import error details: {str(e)}")
        raise e

# Get the Document class from the docx module
Document = import_docx()

def get_document_path(class_name, subject):
    """Get the document path for a specific class and subject"""
    # Try to find a document in the class folder: documents/{class}/{subject}.docx
    class_dir = os.path.join(DOCUMENTS_DIR, class_name)
    doc_filename = f"{subject.replace(' ', '_')}.docx"
    doc_path = os.path.join(class_dir, doc_filename)
    
    # If specific document doesn't exist, try to use a general document for the subject
    if not os.path.exists(doc_path):
        doc_path = os.path.join(DOCUMENTS_DIR, f"{subject.replace(' ', '_')}.docx")
    
    # If still not found, use a default document
    if not os.path.exists(doc_path):
        doc_path = os.path.join(DOCUMENTS_DIR, "axonichealth.docx")  # Default document
    
    return doc_path

def load_and_chunk_docx(path):
    """Loads a DOCX file and splits it into chunks."""
    doc = Document(path)
    full_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    
    if not full_text.strip():
        raise ValueError("Document is empty")
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return splitter.split_text(full_text)

def create_vector_store(class_name, subject):
    """Create a vector store for a specific class and subject"""
    doc_path = get_document_path(class_name, subject)
    
    if not os.path.exists(doc_path):
        raise FileNotFoundError(f"No document found for {subject} in Class {class_name}")
    
    # Load and chunk the document
    chunks = load_and_chunk_docx(doc_path)
    
    # Create embeddings and vector store
    embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)
    
    # Create directory structure: vectorstore/{class}/{subject}/
    vector_class_dir = os.path.join(VECTOR_DIR, class_name)
    vector_subject_dir = os.path.join(vector_class_dir, subject)
    
    # Remove existing vector store if it exists to avoid conflicts
    if os.path.exists(vector_subject_dir):
        shutil.rmtree(vector_subject_dir)
    
    os.makedirs(vector_subject_dir, exist_ok=True)
    
    vectordb = FAISS.from_texts(chunks, embedding)
    vectordb.save_local(vector_subject_dir)
    
    with open(os.path.join(vector_subject_dir, "index.pkl"), "wb") as f:
        pickle.dump(chunks, f)
    
    return vectordb

def load_vector_store(class_name, subject):
    """Load an existing vector store for a specific class and subject"""
    vector_subject_dir = os.path.join(VECTOR_DIR, class_name, subject)
    
    if not os.path.exists(os.path.join(vector_subject_dir, "index.faiss")):
        return None
    
    embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)
    
    # Try to load the vector store with different approaches
    try:
        # First try: New API with allow_dangerous_deserialization
        db = FAISS.load_local(
            folder_path=vector_subject_dir,
            embeddings=embedding,
            allow_dangerous_deserialization=True
        )
        return db
    except Exception as e1:
        try:
            # Second try: Old API without allow_dangerous_deserialization
            db = FAISS.load_local(
                folder_path=vector_subject_dir,
                embeddings=embedding
            )
            return db
        except Exception as e2:
            try:
                # Third try: Direct load with index.faiss (older API)
                index_path = os.path.join(vector_subject_dir, "index.faiss")
                if os.path.exists(index_path):
                    # Try the older API that takes two arguments: path and embeddings
                    db = FAISS.load_local(
                        index_path,
                        embedding,
                        allow_dangerous_deserialization=True
                    )
                    return db
            except Exception as e3:
                st.error(f"Error loading vector store: {str(e1)}")
                return None

def vector_store_exists(class_name, subject):
    """Check if a vector store already exists for a specific class and subject"""
    vector_subject_dir = os.path.join(VECTOR_DIR, class_name, subject)
    return os.path.exists(os.path.join(vector_subject_dir, "index.faiss"))

def handle_file_upload(class_name, subject):
    """Handle vector store creation and caching"""
    key = (class_name, subject)
    
    # Check if vector store is already in session state
    if key in st.session_state.vector_stores:
        return "loaded"
    
    # Check if vector store exists on disk
    if vector_store_exists(class_name, subject):
        vector_store = load_vector_store(class_name, subject)
        if vector_store:
            st.session_state.vector_stores[key] = vector_store
            return "loaded"
    
    # Create new vector store
    try:
        vector_store = create_vector_store(class_name, subject)
        st.session_state.vector_stores[key] = vector_store
        return "created"
    except Exception as e:
        st.error(f"Error creating knowledge base: {str(e)}")
        return None

def generate_answer(query, class_name, subject):
    """Generate an answer for a given query using the vector store"""
    key = (class_name, subject)
    
    # Ensure vector store is loaded
    if key not in st.session_state.vector_stores:
        handle_file_upload(class_name, subject)
    
    if key not in st.session_state.vector_stores:
        return "Error: Could not load knowledge base. Please check if documents exist."
    
    # Create retriever and LLM
    retriever = st.session_state.vector_stores[key].as_retriever()
    llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash", google_api_key=GOOGLE_API_KEY)
    
    # Create prompt template
    prompt_template = PromptTemplate.from_template(
        f"You are a helpful AI tutor for {subject} in Class {class_name}. "
        "Follow this priority when answering:\n"
        "1. Use the provided context as the primary source.\n"
        "2. If the context is insufficient or irrelevant, use your own knowledge "
        "ONLY for:\n"
        "   - Basic mathematics (simple calculations, formulas)\n"
        "   - Grammar\n"
        "   - General science\n"
        "3. If neither context nor allowed knowledge applies, respond with 'I don't have enough information to answer that.'\n\n"
        "Keep answers concise, accurate, and educational.\n\n"
        "Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    )
    
    # Create and run the QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt_template}
    )
    
    try:
        response = qa_chain.invoke({"query": query})
        return response["result"]
    except Exception as e:
        return f"Error generating answer: {str(e)}"
