
import streamlit as st
import ui
import rag

def main():
    st.set_page_config(page_title="Subject-based Q&A", layout="wide")
    #  heading with icon
    st.markdown(
    """
    <h1 style='text-align: center; color: #4CAF50;'>
        📘 Balvidya <span style='color:#FF5722;'>AI</span>   
    </h1>
    <h4 style='text-align: center; color: gray;'>
         Connecting Knowledge with AI  <br>  
    </h4>
    <div style='position: fixed; bottom: 0px; left: 60%; transform: translateX(-50%); 
            width: 100%; text-align: center; z-index: 9999;'>
    <p style='color: #888; font-size: 14px; margin-top: 5px;'>
        Developed by <b>Dnyaneshwar</b>
        <a href='https://github.com/your-github-username' target='_blank'>
            <img src='https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg' 
                 alt='GitHub' width='16' 
                 style='vertical-align: middle; margin-left: 6px; filter: brightness(0) invert(1); transition: 0.3s;'/>
        </a>
    </p>
</div>

<style>
    a img:hover {
        transform: scale(1.2);
        filter: brightness(0) saturate(100%) invert(49%) sepia(91%) saturate(355%) hue-rotate(89deg) brightness(95%) contrast(95%);
    }
</style>


    """,
        unsafe_allow_html=True
    )
    
    # Initialize session state variables
    if 'vector_stores' not in st.session_state:
        st.session_state.vector_stores = {}  # Stores vector stores by (class, subject) key
    if 'chat_histories' not in st.session_state:
        st.session_state.chat_histories = {}  # Stores chat histories by (class, subject) key
    if 'current_class' not in st.session_state:
        st.session_state.current_class = None
    if 'current_subject' not in st.session_state:
        st.session_state.current_subject = None
    
    # Render the UI
    ui.render_sidebar()
    ui.render_chat_interface()
    
    # Handle vector store loading if needed
    if st.session_state.current_class and st.session_state.current_subject:
        key = (st.session_state.current_class, st.session_state.current_subject)
        if key not in st.session_state.vector_stores:
            with st.spinner(f"Preparing knowledge base for {st.session_state.current_subject} in Class {st.session_state.current_class}..."):
                status = rag.handle_file_upload(st.session_state.current_class, st.session_state.current_subject)
                if status:
                    if status == "created":
                        st.success(f"Created new knowledge base for {st.session_state.current_subject} in Class {st.session_state.current_class}")
                    else:
                        st.info(f"Loaded existing knowledge base for {st.session_state.current_subject} in Class {st.session_state.current_class}")
    
if __name__ == "__main__":
    main()
