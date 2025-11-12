import streamlit as st
from src.rag_pipeline import create_or_load_vectorstore, get_qa_chain
from src.pdf_loader import extract_text_from_pdf, extract_methods_section
from src.gemini_wrapper import call_gemini
import os
from datetime import datetime

st.set_page_config(
    page_title="Research Pilot AI", 
    page_icon="�", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Custom CSS Theme
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Main Background with Gradient */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid #334155;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        color: #f1f5f9;
    }
    
    /* Title Styling */
    h1 {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 3rem !important;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    /* Header Styling */
    h2, h3 {
        color: #e2e8f0 !important;
        font-weight: 600;
    }
    
    /* Card Containers */
    .stMarkdown div[data-testid="stMarkdownContainer"] > div {
        background: transparent;
        border: none;
        border-radius: 16px;
        padding: 0;
    }
    
    /* Remove black backgrounds from all containers */
    div[data-testid="stVerticalBlock"] > div {
        background: transparent !important;
    }
    
    div[data-testid="stHorizontalBlock"] > div {
        background: transparent !important;
    }
    
    section[data-testid="stSidebar"] > div {
        background: transparent !important;
    }
    
    /* Radio Buttons - Modern Toggle Style */
    [data-testid="stRadio"] > div {
        background: rgba(15, 23, 42, 0.6);
        border-radius: 12px;
        padding: 0.5rem;
        border: 1px solid #334155;
    }
    
    [data-testid="stRadio"] label {
        background: transparent;
        color: #94a3b8;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        transition: all 0.3s ease;
        font-weight: 500;
    }
    
    [data-testid="stRadio"] label:hover {
        background: rgba(59, 130, 246, 0.1);
        color: #3b82f6;
    }
    
    [data-testid="stRadio"] label[data-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] {
        background: transparent;
        border: 2px dashed #475569;
        border-radius: 16px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #3b82f6;
        background: rgba(59, 130, 246, 0.05);
    }
    
    [data-testid="stFileUploader"] section {
        background: transparent !important;
        border: none !important;
    }
    
    [data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] {
        background: transparent !important;
    }
    
    [data-testid="stFileUploader"] button {
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid #475569;
        color: #e2e8f0;
    }
    
    [data-testid="stFileUploader"] button:hover {
        background: rgba(59, 130, 246, 0.2);
        border-color: #3b82f6;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        width: 100%;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(59, 130, 246, 0.5);
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
    }
    
    .stButton button:active {
        transform: translateY(0);
    }
    
    /* Text Input */
    .stTextInput input {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid #475569;
        border-radius: 12px;
        color: #f1f5f9;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        outline: none;
    }
    
    /* Success/Warning/Info Messages */
    .stSuccess {
        background: rgba(34, 197, 94, 0.1);
        border-left: 4px solid #22c55e;
        border-radius: 8px;
        color: #86efac;
    }
    
    .stWarning {
        background: rgba(251, 191, 36, 0.1);
        border-left: 4px solid #fbbf24;
        border-radius: 8px;
        color: #fde047;
    }
    
    .stInfo {
        background: rgba(59, 130, 246, 0.1);
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
        color: #93c5fd;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid #334155;
        border-radius: 12px;
        color: #e2e8f0;
        font-weight: 500;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #3b82f6;
        background: rgba(59, 130, 246, 0.05);
    }
    
    /* Text Areas */
    .stTextArea textarea {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid #334155;
        border-radius: 12px;
        color: #f1f5f9;
        font-family: 'Fira Code', monospace;
    }
    
    /* Download Button */
    .stDownloadButton button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
    }
    
    .stDownloadButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(16, 185, 129, 0.5);
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #3b82f6 transparent transparent transparent;
    }
    
    /* Column Dividers */
    [data-testid="column"] {
        background: transparent;
        border-radius: 16px;
        padding: 1rem;
    }
    
    /* Header containers */
    [data-testid="stHeader"] {
        background: transparent !important;
    }
    
    /* Block containers */
    .block-container {
        background: transparent !important;
    }
    
    /* File uploader delete buttons */
    [data-testid="stFileUploader"] [data-testid="stFileUploaderDeleteBtn"] {
        color: #ef4444;
    }
    
    [data-testid="stFileUploader"] [data-testid="stFileUploaderDeleteBtn"]:hover {
        color: #dc2626;
        background: rgba(239, 68, 68, 0.1);
    }
    
    /* File uploader file info */
    [data-testid="stFileUploader"] small {
        color: #94a3b8;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0f172a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
    }
    
    /* Caption Text */
    .caption {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: -0.5rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    /* Center section headers */
    .section-header {
        text-align: center;
        color: #e2e8f0;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    /* Answer Card Styling */
    .answer-card {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 16px;
        padding: 2rem;
        color: #f1f5f9;
        box-shadow: 0 10px 30px rgba(59, 130, 246, 0.2);
        backdrop-filter: blur(10px);
        overflow-x: auto;
        word-wrap: break-word;
    }
    
    /* Markdown tables inside answer cards */
    .answer-card table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
        font-size: 0.9rem;
        background: rgba(15, 23, 42, 0.6);
        border-radius: 8px;
        overflow: hidden;
    }
    
    .answer-card table thead tr {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.3) 0%, rgba(139, 92, 246, 0.3) 100%);
        color: #e2e8f0;
        text-align: left;
        font-weight: 600;
    }
    
    .answer-card table th,
    .answer-card table td {
        padding: 0.75rem 1rem;
        border: 1px solid rgba(71, 85, 105, 0.5);
    }
    
    .answer-card table tbody tr {
        border-bottom: 1px solid rgba(71, 85, 105, 0.3);
    }
    
    .answer-card table tbody tr:hover {
        background: rgba(59, 130, 246, 0.1);
    }
    
    .answer-card table tbody tr:last-child {
        border-bottom: none;
    }
    
    .answer-card h2, .answer-card h3, .answer-card h4 {
        color: #93c5fd;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }
    
    .answer-card p {
        line-height: 1.7;
        margin-bottom: 1rem;
    }
    
    .answer-card ul, .answer-card ol {
        margin-left: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .answer-card li {
        margin-bottom: 0.5rem;
        line-height: 1.6;
    }
    
    .answer-card code {
        background: rgba(15, 23, 42, 0.8);
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-family: 'Fira Code', monospace;
        font-size: 0.9em;
    }
    
    .answer-card pre {
        background: rgba(15, 23, 42, 0.8);
        padding: 1rem;
        border-radius: 8px;
        overflow-x: auto;
        margin: 1rem 0;
    }
    
    /* Question Suggestion Buttons */
    div[data-testid="stButton"].question-btn button {
        background: rgba(30, 41, 59, 0.6);
        color: #e2e8f0;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        font-size: 0.95rem;
        font-weight: 500;
        margin-bottom: 0.75rem;
        width: 100%;
        text-align: left;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    div[data-testid="stButton"].question-btn button:hover {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%);
        border-color: #3b82f6;
        transform: translateX(5px);
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }
    
    /* Workspace Management Buttons */
    [data-testid="stSidebar"] .stButton button {
        font-size: 0.85rem !important;
        padding: 0.6rem 1rem !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    /* Expander Styling */
    [data-testid="stExpander"] {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid #334155;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    
    [data-testid="stExpander"] summary {
        font-weight: 600;
        color: #e2e8f0;
        padding: 0.75rem 1rem;
    }
    
    /* Column Layout Fixes */
    [data-testid="column"] {
        padding: 0 0.25rem !important;
    }
    
    /* Sidebar Width Management */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        max-width: 100%;
        overflow-x: hidden;
    }
    
    /* Workspace Card Styling */
    [data-testid="stSidebar"] .stMarkdown {
        overflow-wrap: break-word;
        word-break: break-word;
    }
</style>
""", unsafe_allow_html=True)

# Hero Title with Animation
st.markdown("""
    <h1 style='text-align: center; margin-bottom: 0;'>
        🚀 Research Pilot AI
    </h1>
    <p style='text-align: center; color: #94a3b8; font-size: 1.2rem; margin-top: 0;'>
        Your Intelligent Research Companion
    </p>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 🎯 Navigation")
    mode = st.radio(
        "",
        ["Ask Question", "Compare Two Papers", "Literature Review Generator", "Dataset / Metric Extractor"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # === Workspace Management ===
    st.markdown("### 💾 Workspace Manager")
    
    from src.workspace_manager import WorkspaceManager, collect_current_session_data, restore_session_data
    
    workspace_mgr = WorkspaceManager()
    
    # Initialize history states if not exists
    if "qa_history" not in st.session_state:
        st.session_state["qa_history"] = []
    if "comparison_results" not in st.session_state:
        st.session_state["comparison_results"] = []
    if "literature_reviews" not in st.session_state:
        st.session_state["literature_reviews"] = []
    if "dataset_extractions" not in st.session_state:
        st.session_state["dataset_extractions"] = []
    
    # Save Workspace Section
    with st.expander("💾 Save Current Session", expanded=False):
        st.info("💡 Each save creates a timestamped version so you never lose previous work!")
        
        workspace_name = st.text_input(
            "Workspace Name",
            placeholder="My Research Project",
            key="workspace_name_input",
            help="Multiple saves with the same name will be versioned with timestamps"
        )
        
        if st.button("💾 Save Workspace", use_container_width=True):
            if workspace_name.strip():
                session_data = collect_current_session_data()
                if workspace_mgr.save_workspace(workspace_name, session_data):
                    st.success(f"✅ Workspace '{workspace_name}' saved!")
                    st.rerun()
            else:
                st.warning("⚠️ Please enter a workspace name")
    
    # Load Workspace Section
    with st.expander("� Load Saved Session", expanded=False):
        workspaces = workspace_mgr.list_workspaces()
        
        if workspaces:
            st.markdown(f"**{len(workspaces)} saved workspace(s)**")
            
            for idx, ws in enumerate(workspaces):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    # Format date
                    try:
                        date_str = datetime.fromisoformat(ws['created_at']).strftime("%b %d, %Y %I:%M %p")
                    except:
                        date_str = ws['created_at']
                    
                    st.markdown(f"**{ws['name']}**")
                    st.caption(f"📅 {date_str}")
                
                with col2:
                    if st.button("📂", key=f"load_{idx}", help="Load"):
                        data = workspace_mgr.load_workspace(ws['filename'])
                        if data:
                            restore_session_data(data)
                            st.success(f"✅ Loaded '{ws['name']}'")
                            st.rerun()
                
                with col3:
                    if st.button("🗑️", key=f"delete_{idx}", help="Delete"):
                        if workspace_mgr.delete_workspace(ws['filename']):
                            st.success("✅ Deleted!")
                            st.rerun()
                
                # Download button
                export_data = workspace_mgr.export_workspace(ws['filename'])
                if export_data:
                    st.download_button(
                        label="⬇️ Export",
                        data=export_data,
                        file_name=ws['filename'],
                        mime="application/json",
                        key=f"export_{idx}",
                        use_container_width=True
                    )
                
                st.markdown("---")
        else:
            st.info("No saved workspaces yet")
    
    # Import Workspace Section
    with st.expander("📥 Import Workspace", expanded=False):
        imported_file = st.file_uploader(
            "Upload workspace JSON",
            type=["json"],
            key="import_workspace"
        )
        
        if imported_file and st.button("📥 Import", use_container_width=True):
            if workspace_mgr.import_workspace(imported_file):
                st.success("✅ Workspace imported!")
                st.rerun()
    
    # Clear Storage Section
    with st.expander("🗑️ Clear Storage", expanded=False):
        st.warning("⚠️ This will delete ALL saved workspaces permanently!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear All", use_container_width=True, type="primary"):
                if 'confirm_clear_all' not in st.session_state:
                    st.session_state.confirm_clear_all = True
                    st.rerun()
        
        with col2:
            if st.button("🔄 Clear Session", use_container_width=True):
                # Clear all session state data
                for key in ['uploaded_pdfs', 'qa_history', 'comparison_results', 
                           'literature_reviews', 'dataset_extractions']:
                    if key in st.session_state:
                        st.session_state[key] = [] if key == 'uploaded_pdfs' else []
                
                # Clear temp_data and vectorstore
                if os.path.exists("temp_data"):
                    shutil.rmtree("temp_data")
                    os.makedirs("temp_data")
                if os.path.exists("vectorstore"):
                    shutil.rmtree("vectorstore")
                    os.makedirs("vectorstore")
                
                st.success("✅ Current session cleared!")
                st.rerun()
        
        # Confirmation dialog for clear all
        if st.session_state.get('confirm_clear_all', False):
            st.error("🚨 Are you absolutely sure? This cannot be undone!")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Confirm", use_container_width=True):
                    if workspace_mgr.clear_all_workspaces():
                        st.session_state.confirm_clear_all = False
                        st.success("✅ All workspaces deleted!")
                        st.rerun()
            
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.confirm_clear_all = False
                    st.rerun()
    
    st.markdown("---")
    
    st.markdown("### �💡 Quick Tips")
    st.info("📄 Upload PDFs directly — no file storage needed!")
    st.info("🤖 Powered by Gemini AI for intelligent analysis")
    st.info("💾 Save your work and continue later!")
    
    st.markdown("---")
    
    st.markdown("### 📊 Features")
    st.markdown("""
    - ✨ Smart Q&A
    - 📑 Paper Comparison  
    - ✍️ Literature Review
    - 📊 Dataset Extraction
    - 💾 Session Management
    """)

# --- Mode 1: Research Question ---
from src.question_suggester import generate_smart_questions
from src.pdf_loader import extract_text_from_pdf
import os, shutil, streamlit as st
from src.rag_pipeline import create_or_load_vectorstore, get_qa_chain

if mode == "Ask Question":
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 class='section-header'>🧠 Intelligent Q&A Assistant</h3>", unsafe_allow_html=True)
    st.markdown("<p class='caption'>Upload research papers and ask questions to get AI-powered insights</p>", unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "📚 Upload Research Papers (PDF)",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload one or more PDF files to analyze"
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

        st.success(f"✅ Successfully indexed {len(uploaded_files)} paper(s)!")

    # === Smart Question Suggestions ===
    if st.session_state["suggested_questions"]:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 💡 Smart Question Suggestions")
        st.markdown("<p class='caption'>Click any question to automatically fill it in</p>", unsafe_allow_html=True)
        
        # Display questions in a nice grid
        for i, q in enumerate(st.session_state["suggested_questions"]):
            if st.button(f"💬 {q}", key=f"qbtn_{i}", use_container_width=True):
                st.session_state["query_input"] = q
                st.rerun()

    # === Query Input & Answer ===
    st.markdown("<br>", unsafe_allow_html=True)
    query = st.text_input(
        "🔍 Ask Your Research Question",
        placeholder="Type your question or select one from suggestions above...",
        key="query_input"
    )

    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        search_btn = st.button("🚀 Search", use_container_width=True)

    if search_btn:
        if not os.path.exists("vectorstore"):
            st.warning("⚠️ Please upload and index PDFs first!")
        elif not query.strip():
            st.warning("⚠️ Please enter or select a question.")
        else:
            try:
                with st.spinner("🤔 Analyzing papers and generating answer..."):
                    chain = get_qa_chain()
                    response = chain(query)

                # Save to history
                st.session_state["qa_history"].append({
                    "question": query,
                    "answer": response,
                    "timestamp": datetime.now().isoformat(),
                    "papers": st.session_state.get("last_uploaded", [])
                })

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("### 🎯 Answer")
                st.markdown('<div class="answer-card">', unsafe_allow_html=True)
                st.markdown(response)
                st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(str(e))
                st.info("💡 Tip: If the API is overloaded, please wait a few moments and try again.")
    
    # Display Q&A History
    if st.session_state.get("qa_history"):
        with st.expander(f"📜 View Q&A History ({len(st.session_state['qa_history'])} questions)", expanded=False):
            for idx, item in enumerate(reversed(st.session_state["qa_history"])):
                st.markdown(f"**Q{len(st.session_state['qa_history']) - idx}:** {item['question']}")
                st.markdown(f"*Papers: {', '.join(item.get('papers', []))}*")
                with st.container():
                    st.markdown(item['answer'][:200] + "..." if len(item['answer']) > 200 else item['answer'])
                st.markdown("---")


# --- Mode 2: Compare Two Papers ---
elif mode == "Compare Two Papers":
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 class='section-header'>📑 Methodology Analysis & Comparison</h3>", unsafe_allow_html=True)
    st.markdown("<p class='caption'>Upload one paper for detailed analysis or two papers for side-by-side comparison</p>", unsafe_allow_html=True)
    
    # Display previous comparison results from loaded workspace
    if st.session_state.get("comparison_results"):
        with st.expander("📊 Previous Comparisons", expanded=False):
            for idx, comp_data in enumerate(reversed(st.session_state["comparison_results"])):
                st.markdown(f"### Comparison #{len(st.session_state['comparison_results']) - idx}")
                st.caption(f"📅 {datetime.fromisoformat(comp_data['timestamp']).strftime('%b %d, %Y %I:%M %p')}")
                
                # Handle different comparison types
                if comp_data.get('type') == 'single_paper_analysis':
                    st.caption(f"📄 Paper: {comp_data['paper']}")
                elif comp_data.get('type') == 'two_paper_comparison':
                    st.caption(f"📄 Papers: {comp_data['paper1']} vs {comp_data['paper2']}")
                
                st.markdown('<div class="answer-card">', unsafe_allow_html=True)
                st.markdown(comp_data['result'])
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        file1 = st.file_uploader("📄 Paper 1", type=["pdf"], key="file1")
    with col2:
        file2 = st.file_uploader("📄 Paper 2 (Optional)", type=["pdf"], key="file2")

    # Handle single paper case
    if file1 and not file2:
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            analyze_btn = st.button("🔬 Analyze Methodology", use_container_width=True)
        
        if analyze_btn:
            with st.spinner("🔍 Extracting and analyzing methodology in detail..."):
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

                try:
                    response = call_gemini("Analyze research methodology", detail_prompt)
                    
                    # Save to history
                    st.session_state["comparison_results"].append({
                        "type": "single_paper_analysis",
                        "paper": file1.name,
                        "result": response,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # --- Render Detailed Analysis ---
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("### 🔬 Detailed Methodology Analysis")
                    st.markdown('<div class="answer-card">', unsafe_allow_html=True)
                    st.markdown(response)
                    st.markdown('</div>', unsafe_allow_html=True)

                    with st.expander("📄 View Raw Extracted Methods Section"):
                        st.subheader(file1.name)
                        st.text_area("Extracted Methods", methods1, height=300, label_visibility="collapsed")
                        
                except Exception as e:
                    st.error(str(e))
                    st.info("💡 Tip: If the API is overloaded, please wait a few moments and try again.")

    # Handle two paper comparison case
    elif file1 and file2:
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            compare_btn = st.button("⚖️ Compare Methods", use_container_width=True)
        
        if compare_btn:
            with st.spinner("🔄 Extracting and comparing methodologies..."):
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

                try:
                    response = call_gemini("Compare research methodologies", compare_prompt)

                    # Save to history
                    st.session_state["comparison_results"].append({
                        "type": "two_paper_comparison",
                        "paper1": file1.name,
                        "paper2": file2.name,
                        "result": response,
                        "timestamp": datetime.now().isoformat()
                    })

                    # --- Render Table Output ---
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("### 🧩 Methodology Comparison Table")
                    
                    # Wrap in a container div with custom styling
                    st.markdown('<div class="answer-card">', unsafe_allow_html=True)
                    st.markdown(response)  # Let Streamlit render the Markdown table
                    st.markdown('</div>', unsafe_allow_html=True)

                    with st.expander("🔬 View Raw Extracted Methods"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader(file1.name)
                            st.text_area("Paper 1 Methods", methods1, height=200, label_visibility="collapsed")
                        with col2:
                            st.subheader(file2.name)
                            st.text_area("Paper 2 Methods", methods2, height=200, label_visibility="collapsed")
                            
                except Exception as e:
                    st.error(str(e))
                    st.info("💡 Tip: If the API is overloaded, please wait a few moments and try again.")


# --- Literature Review Generator ---
elif mode == "Literature Review Generator":
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 class='section-header'>✍️ Auto Literature Review Generator</h3>", unsafe_allow_html=True)
    st.markdown("<p class='caption'>Upload multiple papers to generate a cohesive, academic literature review</p>", unsafe_allow_html=True)
    
    # Display previous literature reviews from loaded workspace
    if st.session_state.get("literature_reviews"):
        with st.expander("📚 Previous Literature Reviews", expanded=False):
            for idx, review_data in enumerate(reversed(st.session_state["literature_reviews"])):
                st.markdown(f"### Review #{len(st.session_state['literature_reviews']) - idx}")
                st.caption(f"📅 {datetime.fromisoformat(review_data['timestamp']).strftime('%b %d, %Y %I:%M %p')}")
                st.caption(f"📄 Papers: {', '.join(review_data['papers'])}")
                st.markdown('<div class="answer-card">', unsafe_allow_html=True)
                st.markdown(review_data['review'])
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.download_button(
                    label="💾 Download Review",
                    data=review_data['review'],
                    file_name=f"literature_review_{idx+1}.txt",
                    mime="text/plain",
                    key=f"download_review_{idx}"
                )
                st.markdown("---")

    uploads = st.file_uploader(
        "📚 Upload Research Papers (2+ PDFs recommended)",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload multiple papers for a comprehensive literature review"
    )

    if uploads:
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            generate_btn = st.button("✨ Generate Review", use_container_width=True)
        
        if generate_btn:
            from src.pdf_loader import extract_text_from_pdf
            from src.literature_review import generate_literature_review

            try:
                with st.spinner("🧠 Reading papers and synthesizing review..."):
                    combined_text = ""
                    for f in uploads:
                        text = extract_text_from_pdf(f.read())
                        # only grab important parts to keep prompt efficient
                        combined_text += f"\n\n=== {f.name} ===\n{text[:2000]}"

                    review = generate_literature_review(combined_text)

                # Save to history
                st.session_state["literature_reviews"].append({
                    "papers": [f.name for f in uploads],
                    "review": review,
                    "timestamp": datetime.now().isoformat()
                })

                st.success("✅ Literature Review Generated Successfully!")
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("### 📝 Your Literature Review")
                st.markdown('<div class="answer-card">', unsafe_allow_html=True)
                st.markdown(review)
                st.markdown('</div>', unsafe_allow_html=True)

                # Optional download button
                st.markdown("<br>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns([2, 1, 2])
                with col2:
                    st.download_button(
                        label="💾 Download as TXT",
                        data=review,
                        file_name="literature_review.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

                with st.expander("📚 View Source Paper Previews"):
                    for idx, f in enumerate(uploads):
                        f.seek(0)
                        st.markdown(f"#### 📄 {f.name}")
                        preview_text = extract_text_from_pdf(f.read())[:1500]
                        st.text_area(f"Preview {idx+1}", preview_text, height=150, label_visibility="collapsed")
                        
            except Exception as e:
                st.error(str(e))
                st.info("💡 Tip: If the API is overloaded, please wait a few moments and try again.")


# --- Dataset / Metric Extractor (Gemini) ---
elif mode == "Dataset / Metric Extractor":
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 class='section-header'>📊 Dataset & Metric Extractor</h3>", unsafe_allow_html=True)
    st.markdown("<p class='caption'>Automatically detect datasets and evaluation metrics using Gemini AI</p>", unsafe_allow_html=True)
    
    # Display previous extractions from loaded workspace
    if st.session_state.get("dataset_extractions"):
        with st.expander("📋 Previous Extractions", expanded=False):
            for idx, extract_data in enumerate(reversed(st.session_state["dataset_extractions"])):
                st.markdown(f"### Extraction #{len(st.session_state['dataset_extractions']) - idx}")
                st.caption(f"📅 {datetime.fromisoformat(extract_data['timestamp']).strftime('%b %d, %Y %I:%M %p')}")
                st.caption(f"📄 Papers: {', '.join(extract_data['papers'])}")
                st.markdown('<div class="answer-card">', unsafe_allow_html=True)
                st.markdown(extract_data['result'])
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.download_button(
                    label="💾 Download Extraction",
                    data=extract_data['result'],
                    file_name=f"dataset_extraction_{idx+1}.txt",
                    mime="text/plain",
                    key=f"download_extract_{idx}"
                )
                st.markdown("---")

    # === File uploader ===
    uploads = st.file_uploader(
        "📂 Upload Research Papers for Analysis",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload papers to extract datasets and metrics automatically"
    )

    # === Action button ===
    if uploads:
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            analyze_btn = st.button("🔍 Analyze Papers", use_container_width=True)
        
        if analyze_btn:
            from src.pdf_loader import extract_text_from_pdf
            from src.dataset_metric_extractor import extract_datasets_and_metrics_with_gemini
            import os

            try:
                with st.spinner("🤖 Analyzing papers with Gemini AI..."):
                    combined_results = ""
                    for f in uploads:
                        # Extract text from each uploaded paper
                        text = extract_text_from_pdf(f.read())

                        # Gemini-powered dataset + metric extraction
                        result = extract_datasets_and_metrics_with_gemini(text)

                        combined_results += f"\n\n## 📄 {f.name}\n{result}"

                # Save to history
                st.session_state["dataset_extractions"].append({
                    "papers": [f.name for f in uploads],
                    "results": combined_results,
                    "timestamp": datetime.now().isoformat()
                })

                st.success("✅ Analysis Complete!")

                # === Display results ===
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("### 🧩 Dataset & Metric Analysis")
                st.markdown('<div class="answer-card">', unsafe_allow_html=True)
                st.markdown(combined_results)
                st.markdown('</div>', unsafe_allow_html=True)

                # === Download button ===
                st.markdown("<br>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns([2, 1, 2])
                with col2:
                    st.download_button(
                        label="💾 Download Results",
                        data=combined_results,
                        file_name="dataset_metric_analysis.md",
                        mime="text/markdown",
                        use_container_width=True
                    )

                # === Optional consolidation summary ===
                with st.spinner("📈 Generating consolidated summary..."):
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

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("### 📈 Consolidated Summary")
                st.markdown('<div class="answer-card">', unsafe_allow_html=True)
                st.markdown(consolidated)
                st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(str(e))
                st.info("💡 Tip: If the API is overloaded, please wait a few moments and try again.")
