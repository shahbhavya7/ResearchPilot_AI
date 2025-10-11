import streamlit as st
from rag_pipeline import get_qa_chain, create_or_load_vectorstore
from pdf_loader import extract_text_from_pdf, extract_methods_section
from gemini_wrapper import call_gemini
import os

st.set_page_config(page_title="📚 PaperPilot", page_icon="🧠", layout="wide")

st.title("📚 PaperPilot ")

# --- Sidebar ---
mode = st.sidebar.radio("Choose mode:", ["Ask Question", "Compare Two Papers"])
st.sidebar.markdown("---")
st.sidebar.info("💡 You can upload PDFs directly — no need to store them in the data folder.")

# --- Mode 1: Research Question ---
if mode == "Ask Question":
    st.header("🧠 Ask a research question")
    uploaded_files = st.file_uploader("Upload one or more PDFs", type=["pdf"], accept_multiple_files=True)

    if uploaded_files:
        with st.spinner("Indexing your uploaded papers..."):
            os.makedirs("temp_data", exist_ok=True)
            for f in uploaded_files:
                with open(os.path.join("temp_data", f.name), "wb") as fp:
                    fp.write(f.read())
            create_or_load_vectorstore("temp_data")
        st.success("✅ Papers indexed successfully!")

    query = st.text_input("Ask your question (e.g., 'What is the paper's main contribution?')")
    if st.button("Search"):
        if not os.path.exists("vectorstore"):
            st.warning("Please upload and index PDFs first!")
        else:
            with st.spinner("Thinking with Gemini..."):
                chain = get_qa_chain()
                response = chain(query)
            st.markdown("### 🧠 Answer:")
            st.markdown(
                f"<div style='background-color:#111827;padding:15px;border-radius:10px;color:#f1f5f9;'>{response}</div>",
                unsafe_allow_html=True
            )

# --- Mode 2: Compare Two Papers ---
elif mode == "Compare Two Papers":
    st.header("📑 Compare Methodology of Two Papers")

    col1, col2 = st.columns(2)
    with col1:
        file1 = st.file_uploader("Upload Paper 1", type=["pdf"], key="file1")
    with col2:
        file2 = st.file_uploader("Upload Paper 2", type=["pdf"], key="file2")

    if file1 and file2:
        if st.button("Compare Methods"):
            with st.spinner("Extracting and analyzing methods..."):
                text1 = extract_text_from_pdf(file1.read())
                text2 = extract_text_from_pdf(file2.read())

                methods1 = extract_methods_section(text1)
                methods2 = extract_methods_section(text2)

                compare_prompt = f"""
You are an expert research analyst. Compare the **Methodology** sections of two research papers.

**Paper 1 Methods:**
{methods1}

**Paper 2 Methods:**
{methods2}

Please produce a **Markdown table** comparison with these exact columns:
| Aspect | Paper 1 Summary | Paper 2 Summary | Key Difference / Insight |

Include aspects like:
- Algorithm / Model Used
- Dataset / Data Source
- Feature Engineering or Preprocessing
- Evaluation Metrics
- Experimental Setup
- Strengths
- Limitations
- Generalization or Novelty

Make sure the table is valid Markdown and readable in Streamlit.
If any information is missing, mark it as "Not mentioned".
"""

                response = call_gemini("Compare research methodologies", compare_prompt)

                # --- Render Table Output ---
                st.markdown("### 🧩 Methodology Comparison Table")

                if "|" in response:  # crude check if Markdown table present
                    st.markdown(response, unsafe_allow_html=True)
                else:
                    st.write(response)

                with st.expander("🔬 Raw Extracted Methods"):
                    st.subheader(file1.name)
                    st.text_area("Paper 1 - Methods", methods1, height=200)
                    st.subheader(file2.name)
                    st.text_area("Paper 2 - Methods", methods2, height=200)

