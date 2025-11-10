# gemini_wrapper.py
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from dotenv import load_dotenv
import os
import time

load_dotenv()
# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def call_gemini(prompt, context, max_retries=3, initial_delay=2):
    """
    Calls Gemini 2.5 Flash model with given context and question.
    Returns the generated answer text.
    Includes retry logic for API overload errors.
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

    for attempt in range(max_retries):
        try:
            response = genai.GenerativeModel("gemini-2.5-flash").generate_content(
                full_prompt
            )
            return response.text
            
        except google_exceptions.ResourceExhausted as e:
            # Model is overloaded
            if attempt < max_retries - 1:
                delay = initial_delay * (2 ** attempt)  # Exponential backoff
                time.sleep(delay)
                continue
            else:
                raise Exception(
                    "⚠️ Gemini API is currently overloaded. Please try again in a few moments. "
                    "If this persists, consider using a smaller document or fewer papers."
                ) from e
                
        except google_exceptions.DeadlineExceeded as e:
            # Timeout error
            if attempt < max_retries - 1:
                delay = initial_delay * (2 ** attempt)
                time.sleep(delay)
                continue
            else:
                raise Exception(
                    "⚠️ Request timeout. The document might be too large. "
                    "Try uploading smaller PDFs or fewer papers at once."
                ) from e
                
        except google_exceptions.InvalidArgument as e:
            # Invalid input (usually too long)
            raise Exception(
                "⚠️ The input is too large for the API. "
                "Please try with shorter documents or fewer papers."
            ) from e
            
        except Exception as e:
            # Other errors
            if attempt < max_retries - 1:
                delay = initial_delay * (2 ** attempt)
                time.sleep(delay)
                continue
            else:
                raise Exception(
                    f"⚠️ An error occurred while calling Gemini API: {str(e)}\n"
                    "Please try again or contact support if the issue persists."
                ) from e
    
    raise Exception("⚠️ Failed to get response after multiple retries. Please try again later.")
