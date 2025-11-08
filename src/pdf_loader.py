# pdf_loader.py
import fitz
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter

def extract_text_from_pdf(pdf_path_or_bytes):
    """
    Works with file path or uploaded file bytes.
    """
    text = ""
    if isinstance(pdf_path_or_bytes, bytes):
        with fitz.open(stream=pdf_path_or_bytes, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text("text")
    else:
        with fitz.open(pdf_path_or_bytes) as doc:
            for page in doc:
                text += page.get_text("text")
    return text

def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)
    return splitter.split_text(text)

def extract_methods_section(text):
    """
    Extracts the 'Methodology' or 'Methods' section using regex.
    """
    pattern = r"(?:Methodology|Methods|Materials and Methods)([\s\S]*?)(?:Results|Experiments|Discussion|Conclusion|References|Bibliography)"
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else "No distinct methods section found."
