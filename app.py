import streamlit as st
from rag_pipeline import get_qa_chain, create_or_load_vectorstore
from pdf_loader import extract_text_from_pdf, extract_methods_section
from gemini_wrapper import call_gemini
import os

st.set_page_config(page_title="📚 PaperPilot", page_icon="🧠", layout="wide")

st.title("📚 Research Pilot ")

# --- Sidebar ---
mode = st.sidebar.radio("Choose mode:", ["Ask Question", "Compare Two Papers"])
st.sidebar.markdown("---")
st.sidebar.info("💡 You can upload PDFs directly — no need to store them in the data folder.")

# --- Mode 1: Research Question ---
from question_suggester import generate_smart_questions
from pdf_loader import extract_text_from_pdf
import os, shutil, streamlit as st
from rag_pipeline import create_or_load_vectorstore, get_qa_chain

if mode == "Ask Question":
    st.header("🧠 Ask a Research Question")
    uploaded_files = st.file_uploader(
        "Upload one or more PDFs", type=["pdf"], accept_multiple_files=True
    )

    # Initialize session state for questions
    if "suggested_questions" not in st.session_state:
        st.session_state["suggested_questions"] = []
    if "query_input" not in st.session_state:
        st.session_state["query_input"] = ""

    # === Upload & Index PDFs ===
    if uploaded_files:
        with st.spinner("📚 Indexing and analyzing your uploaded papers..."):
            # Only regenerate questions if new PDFs uploaded
            uploaded_names = [f.name for f in uploaded_files]
            if st.session_state.get("last_uploaded") != uploaded_names:
                if os.path.exists("temp_data"):
                    shutil.rmtree("temp_data")
                os.makedirs("temp_data", exist_ok=True)

                combined_text = ""
                for f in uploaded_files:
                    path = os.path.join("temp_data", f.name)
                    with open(path, "wb") as fp:
                        fp.write(f.read())
                    f.seek(0)
                    text = extract_text_from_pdf(f.read())
                    combined_text += text[:3000]

                create_or_load_vectorstore("temp_data")

                with st.spinner("🤖 Generating smart questions..."):
                    st.session_state["suggested_questions"] = generate_smart_questions(
                        combined_text, n=5
                    )
                st.session_state["last_uploaded"] = uploaded_names

        st.success(f"✅ Indexed {len(uploaded_files)} paper(s)!")

    # === Smart Question Suggestions ===
    if st.session_state["suggested_questions"]:
        st.markdown("#### 💡 Smart Question Suggestions:")
        st.markdown("""
        <style>
        /* --- Elegant Streamlit-Themed Buttons --- */
        div[data-testid="stButton"] button {
            background-color: #1b1f24;  /* near the Streamlit dark background */
            color: #e5e7eb;             /* soft gray-white text */
            border: 1px solid #2d3138;
            border-radius: 8px;
            padding: 0.6rem 1rem;
            font-size: 0.9rem;
            font-weight: 500;
            margin-bottom: 0.4rem;
            width: 100%;
            text-align: left;
            transition: all 0.15s ease-in-out;
        }

        /* Hover: gentle brightness + lift */
        div[data-testid="stButton"] button:hover {
            background-color: #2a2f36;
            color: #f9fafb;
            border-color: #3c4047;
            transform: translateY(-1px);
            box-shadow: 0 0 6px rgba(255, 255, 255, 0.06);
        }

        /* Active / Selected button */
        div[data-testid="stButton"] button:focus {
            outline: none;
            background-color: #374151;
            border-color: #475569;
            box-shadow: inset 0 0 0 1px #4b5563;
        }

        /* Compact spacing for stacked layout */
        section.main div.block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)



        # uniform list layout
        for i, q in enumerate(st.session_state["suggested_questions"]):
            if st.button(q, key=f"qbtn_{i}"):
                st.session_state["query_input"] = q

    # === Query Input & Answer ===
    query = st.text_input(
        "Ask your question (or select one above):",
        key="query_input"
    )

    if st.button("Search"):
        if not os.path.exists("vectorstore"):
            st.warning("Please upload and index PDFs first!")
        elif not query.strip():
            st.warning("Please enter or select a question.")
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

