# app.py
import streamlit as st
from rag_pipeline import create_or_load_vectorstore, get_qa_chain
import os

st.set_page_config(page_title="PaperPilot", page_icon="📚")

st.title("📚 PaperPilot: Your Personal Research Copilot")

# Sidebar
with st.sidebar:
    st.header("Setup")
    if st.button("Index PDFs"):
        with st.spinner("Building vector index..."):
            create_or_load_vectorstore()
        st.success("✅ Index created!")

    st.info("Put your PDFs in the `data/` folder before indexing.")

# Main interface
query = st.text_input(
    "Ask a research question (e.g., 'What loss functions are used in summarization?')"
)

if st.button("Search"):
    if not os.path.exists("vectorstore"):
        st.warning("⚠️ Please index PDFs first!")
    elif query.strip() == "":
        st.warning("Please enter a question first.")
    else:
        qa_chain = get_qa_chain()   # returns our Gemini-based function
        with st.spinner("🤔 Thinking..."):
            try:
                response = qa_chain(query)   # directly call the function
                st.markdown("### 🧠 Answer:")
                st.write(response)
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
