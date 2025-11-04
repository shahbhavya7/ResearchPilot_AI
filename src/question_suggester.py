# question_suggester.py
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_smart_questions(paper_text: str, n: int = 5):
    """
    Use Gemini 2.5 Pro to generate intelligent research questions.
    """
    if not paper_text or len(paper_text.strip()) < 100:
        return []

    prompt = f"""
You are an expert research assistant.
Read the following text from a research paper and generate {n} insightful, diverse questions 
that a researcher might ask to better understand the paper.

Focus on methods, results, datasets, evaluation, and innovation aspects.

Text:
{paper_text[:2000]}

Return only a numbered list of questions.
"""

    try:
        model = genai.GenerativeModel("gemini-2.5-pro")
        response = model.generate_content(prompt)
        text = response.text
        questions = [q.strip("•- \n") for q in text.split("\n") if "?" in q]
        return questions[:n]
    except Exception as e:
        print("Gemini error:", e)
        return []
