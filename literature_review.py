# literature_review.py
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_literature_review(papers_text: str) -> str:
    """
    Generate a concise, structured literature review paragraph across multiple papers.
    """
    if not papers_text.strip():
        return "No text available for review generation."

    prompt = f"""
You are a senior academic researcher.
Given excerpts from several papers (abstracts, intros, or conclusions),
write a **concise literature review paragraph** that:
- Summarizes common themes and contributions,
- Identifies differences in approaches,
- Notes research gaps or future opportunities,
- Uses academic tone (formal but readable).

Keep it under 250 words.
Text from papers:
{papers_text[:16000]}
    """

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating review: {e}"
