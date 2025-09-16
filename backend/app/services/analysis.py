import os
from io import BytesIO
from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from pypdf import PdfReader

from app.core.config import settings


INSIGHTS_PROMPT_TEMPLATE = """
You are a customer interview analyst helping extract key insights from product-related customer conversations. Exclude information unrelated to the product.

Product: {product_description}

Task: Analyze the interview transcript and extract all relevant insights, classifying them by category:
1. #pain — what the user dislikes, finds annoying, or difficult.
2. #feature — requests for new features or improvements.
3. #bug — what doesn't work or works incorrectly.
4. #feedback — opinions about existing features (like/dislike).
5. #insight — unexpected comments or hidden needs.

Output format:
- Each insight starts with a tag (e.g., #pain).
- After the tag, a quote from the interview (verbatim or close to the original).
- Then a brief interpretation (what exactly is the pain/request/problem).
If there's emotional tone (frustration, enthusiasm), mention it in parentheses.

Example:
#pain "I constantly forget to save links, and then can't find them" – No convenient way to quickly save links (frustration).

#feature "I’d like the bot to suggest categories for tasks" – Request for AI suggestions when creating tasks.

#insight "I rarely use voice input because I’m afraid to make mistakes" – Hidden fear of errors when using voice input.

Important:
- Include even indirect complaints ("I have to copy manually" → #pain).
- Note strong emotions (e.g., "This is just terrible!").
- Don’t add generic phrases with no specifics.
- Follow the example format exactly. Separate each insight with
- Output only structured insights, no other text. \n\n.

Interview transcript:
{transcript}
"""


def _ensure_google_api_key() -> None:
    api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key


def _build_llm() -> ChatGoogleGenerativeAI:
    _ensure_google_api_key()
    model = settings.GEMINI_MODEL or "gemini-1.5-flash"
    return ChatGoogleGenerativeAI(model=model, temperature=0.2)


def analyze_text(text: str, product_description: Optional[str] = None) -> Optional[str]:
    if not text or not text.strip():
        return None
    try:
        llm = _build_llm()
        product = (
            product_description
            or "Telegram bot for organizing tasks (save content by category, reminders, voice/text input)."
        )
        prompt = INSIGHTS_PROMPT_TEMPLATE.format(
            product_description=product,
            transcript=text.strip(),
        )
        result = llm.invoke(prompt)
        content = getattr(result, "content", None)
        if isinstance(content, str):
            return content.strip()
        if isinstance(result, str):
            return result.strip()
        return str(result).strip()
    except Exception:
        return None


def text_from_file(filename: str, content: bytes) -> str:
    name_lower = (filename or "").lower()
    if name_lower.endswith(".pdf"):
        try:
            reader = PdfReader(BytesIO(content))
            text_parts = []
            for page in reader.pages:
                extracted = page.extract_text() or ""
                text_parts.append(extracted)
            return "\n".join(text_parts).strip()
        except Exception:
            # Fallback to raw bytes decode
            return content.decode("utf-8", errors="ignore")
    # Plain text and other light formats
    return content.decode("utf-8", errors="ignore") 