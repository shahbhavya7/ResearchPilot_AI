import streamlit as st
from src.rag_pipeline import create_or_load_vectorstore, get_qa_chain
from src.pdf_loader import extract_text_from_pdf, extract_methods_section
from src.gemini_wrapper import call_gemini
import os

st.set_page_config(page_title="📚 PaperPilot", page_icon="🧠", layout="wide")

st.title("📚 Research Pilot ")

# --- Sidebar ---
mode = st.sidebar.radio("Choose mode:", ["Ask Question", "Compare Two Papers","Literature Review Generator","Dataset / Metric Extractor"])
st.sidebar.markdown("---")
st.sidebar.info("💡 You can upload PDFs directly — no need to store them in the data folder.")

# --- Mode 1: Research Question ---
from src.question_suggester import generate_smart_questions
from src.pdf_loader import extract_text_from_pdf
import os, shutil, streamlit as st
from src.rag_pipeline import create_or_load_vectorstore, get_qa_chain

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
            with st.spinner("Thinking..."):
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
    st.caption("Upload one paper for detailed analysis or two papers for comparison")

    col1, col2 = st.columns(2)
    with col1:
        file1 = st.file_uploader("Upload Paper 1", type=["pdf"], key="file1")
    with col2:
        file2 = st.file_uploader("Upload Paper 2 (Optional)", type=["pdf"], key="file2")

    # Handle single paper case
    if file1 and not file2:
        if st.button("Analyze Methodology"):
            with st.spinner("Extracting and analyzing methodology in detail..."):
                text1 = extract_text_from_pdf(file1.read())
                methods1 = extract_methods_section(text1)

                detail_prompt = f"""
You are an expert research analyst. Provide a **comprehensive and detailed analysis** of the methodology section from this research paper.

**Paper Methods:**
{methods1}

Please structure your analysis as a **detailed Markdown report** covering:

## 🎯 Research Approach
- Overall methodology paradigm (e.g., experimental, theoretical, empirical)
- Research design and framework

## 🔬 Algorithm / Model
- Detailed description of algorithms, models, or techniques used
- Technical specifications and parameters
- Any novel contributions or modifications

## 📊 Dataset & Data Collection
- Dataset(s) used with specifics (size, source, characteristics)
- Data collection methods and preprocessing steps
- Feature engineering or transformation techniques

## 🧪 Experimental Setup
- Hardware/software environment
- Implementation details
- Training/testing procedures
- Hyperparameters and configurations

## 📈 Evaluation Metrics
- All metrics used for evaluation
- Why these metrics were chosen
- Baseline comparisons

## 💪 Strengths
- What makes this methodology robust or innovative
- Key advantages over prior work

## ⚠️ Limitations
- Acknowledged or apparent weaknesses
- Potential biases or constraints
- Scope limitations

## 🔮 Reproducibility & Generalization
- How reproducible is this approach
- Generalization potential to other domains/datasets
- Code/data availability mentioned

If any section is not explicitly mentioned in the paper, note it as "Not explicitly mentioned" but provide reasonable inferences if possible.
"""

                response = call_gemini("Analyze research methodology", detail_prompt)

                # --- Render Detailed Analysis ---
                st.markdown("### 🔬 Detailed Methodology Analysis")
                st.markdown(
                    f"<div style='background-color:#111827;padding:18px;border-radius:12px;color:#f1f5f9;'>{response}</div>",
                    unsafe_allow_html=True
                )

                with st.expander("📄 Raw Extracted Methods Section"):
                    st.subheader(file1.name)
                    st.text_area("Extracted Methods", methods1, height=300)

    # Handle two paper comparison case
    elif file1 and file2:
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

# --- Literature Review Generator ---
elif mode == "Literature Review Generator":
    st.header("✍️ Auto Literature Review Generator")
    st.caption("Upload multiple papers to generate a cohesive literature review paragraph.")

    uploads = st.file_uploader("Upload 2 or more PDFs", type=["pdf"], accept_multiple_files=True)

    if uploads and st.button("Generate Literature Review"):
        from src.pdf_loader import extract_text_from_pdf
        from src.literature_review import generate_literature_review

        with st.spinner("🧠 Reading papers and synthesizing review..."):
            combined_text = ""
            for f in uploads:
                text = extract_text_from_pdf(f.read())
                # only grab important parts to keep prompt efficient
                combined_text += f"\n\n=== {f.name} ===\n{text[:2000]}"

            review = generate_literature_review(combined_text)

        st.success("✅ Literature Review Generated!")
        st.markdown("### 🧩 Literature Review")
        st.markdown(
            f"<div style='background-color:#111827;padding:18px;border-radius:12px;color:#f1f5f9;'>{review}</div>",
            unsafe_allow_html=True
        )

        # Optional download button
        st.download_button(
            label="📄 Download Review as TXT",
            data=review,
            file_name="literature_review.txt",
            mime="text/plain"
        )

        with st.expander("📚 Source Previews"):
            for f in uploads:
                f.seek(0)
                st.text_area(f.name, extract_text_from_pdf(f.read())[:1500], height=150)

# --- Dataset / Metric Extractor (Gemini) ---
elif mode == "Dataset / Metric Extractor":
    st.header("📊 Dataset & Metric Extractor")
    st.caption(
        "Upload one or more research papers (PDFs) and let Research Pilot 2.5 Pro "
        "automatically detect datasets and evaluation metrics — even if only implied."
    )

    # === File uploader ===
    uploads = st.file_uploader(
        "📂 Upload PDFs for Analysis",
        type=["pdf"],
        accept_multiple_files=True,
        help="You can upload multiple papers together to get combined insights."
    )

    # === Action button ===
    if uploads and st.button("🔍 Analyze with Research Pilot"):
        from src.pdf_loader import extract_text_from_pdf
        from src.dataset_metric_extractor import extract_datasets_and_metrics_with_gemini
        import os

        with st.spinner("🤖 Research Pilot is reading and analyzing your uploaded papers..."):
            combined_results = ""
            for f in uploads:
                # Extract text from each uploaded paper
                text = extract_text_from_pdf(f.read())

                # Gemini-powered dataset + metric extraction
                result = extract_datasets_and_metrics_with_gemini(text)

                combined_results += f"\n\n## 📄 {f.name}\n{result}"

        st.success("✅ Research Pilot successfully analyzed all uploaded papers!")

        # === Display results ===
        st.markdown("### 🧩 Combined Dataset & Metric Analysis")
        st.markdown(
            f"<div style='background-color:#111827;padding:18px;border-radius:12px;color:#f1f5f9;'>"
            f"{combined_results}</div>",
            unsafe_allow_html=True
        )

        # === Download button ===
        st.download_button(
            label="💾 Download Results as Markdown",
            data=combined_results,
            file_name="dataset_metric_analysis.md",
            mime="text/markdown"
        )

        # === Optional consolidation summary ===
        with st.spinner("📈 Summarizing dataset and metric trends across all papers..."):
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel("gemini-2.5-pro")

            summary_prompt = f"""
            Combine the following per-paper tables into a unified summary.

            Include:
            - Top datasets and metrics (frequency & domain)
            - Observed trends across papers
            - 2–3 sentence insight summary

            Per-paper details:
            {combined_results}
            """
            consolidated = model.generate_content(summary_prompt).text

        st.markdown("### 📈 Consolidated Summary Across Papers")
        st.markdown(
            f"<div style='background-color:#111827;padding:16px;border-radius:10px;color:#f1f5f9;'>"
            f"{consolidated}</div>",
            unsafe_allow_html=True
        )

