# literature_review.py
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from dotenv import load_dotenv
import os
import time

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_literature_review(papers_text: str, max_retries=3) -> str:
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

    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            return response.text
        except (google_exceptions.ResourceExhausted, google_exceptions.DeadlineExceeded) as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            else:
                raise Exception(
                    "⚠️ Gemini API is currently overloaded. Please try again in a few moments."
                ) from e
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            else:
                raise Exception(f"⚠️ Error generating review: {str(e)}") from e
    
    raise Exception("⚠️ Failed to generate review after multiple retries.")
