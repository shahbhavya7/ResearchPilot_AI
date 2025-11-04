# gemini_wrapper.py
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def call_gemini(prompt, context):
    """
    Calls Gemini 2.5 Pro model with given context and question.
    Returns the generated answer text.
    """
    full_prompt = f"""
You are a helpful AI research assistant.
Use the following document excerpts to answer the user's question.
Cite sources like [filename.pdf] where applicable.
If unsure, say you don't have enough information.

Context:
{context}

Question: {prompt}

Answer:
    """

    response = genai.GenerativeModel("gemini-2.5-flash").generate_content(full_prompt)
    return response.text
