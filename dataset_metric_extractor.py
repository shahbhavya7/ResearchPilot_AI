# gemini_dataset_metric_extractor.py
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def extract_datasets_and_metrics_with_gemini(paper_text: str) -> str:
    """
    Uses Gemini 2.5 Pro to infer datasets and evaluation metrics mentioned in a paper.
    Returns a structured Markdown report (tables).
    """
    if not paper_text or len(paper_text.strip()) < 200:
        return "No text provided."

    prompt = f"""
You are an expert AI research assistant.
Read the following research paper text carefully and extract both:
1. **Datasets** used, mentioned, or implied.
2. **Evaluation metrics** or performance measures mentioned.

For each, produce two clear Markdown tables with the following columns:

### 📊 Datasets
| Dataset Name | Domain/Type | Usage Context | Example Mention (short quote) |

### 📏 Metrics
| Metric Name | Purpose / What It Measures | Example Mention (short quote) |

If any dataset or metric is only implied, mark it with *(inferred)*.
If none are found, explicitly say "No datasets detected." or "No metrics detected."

Paper text:
{paper_text[:12000]}

Respond only with Markdown tables and brief headers — no extra commentary.
"""

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error extracting datasets/metrics: {e}"
