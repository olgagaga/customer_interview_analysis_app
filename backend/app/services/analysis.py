import os
from io import BytesIO
from typing import Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain_google_genai import ChatGoogleGenerativeAI
from pypdf import PdfReader

from app.core.config import settings


ANALYSIS_MAP_PROMPT_TEMPLATE = """
You are an expert product researcher. Analyze the following chunk of a customer interview transcript.
Extract:
- Key pain points
- Jobs-to-be-done
- Feature requests
- Sentiment
- Notable quotes (if any)

Chunk:
"""

ANALYSIS_COMBINE_PROMPT_TEMPLATE = """
You are an expert product researcher. You will be given multiple partial analyses from chunks of the same interview.
Synthesize a single, coherent, non-repetitive report with these sections:
1) Summary (3-5 bullets)
2) Pain points
3) Jobs-to-be-done
4) Feature requests
5) Sentiment (overall and rationale)
6) Key quotes (bullet list)
7) Actionable insights (specific, prioritized)
"""


def _ensure_google_api_key() -> None:
    api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key


def _build_llm() -> ChatGoogleGenerativeAI:
    _ensure_google_api_key()
    model = settings.GEMINI_MODEL or "gemini-1.5-flash"
    return ChatGoogleGenerativeAI(model=model, temperature=0.2)


def analyze_text(text: str) -> Optional[str]:
    if not text or not text.strip():
        return None
    try:
        llm = _build_llm()
        splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=400)
        docs = splitter.create_documents([text])

        map_prompt = PromptTemplate(template=ANALYSIS_MAP_PROMPT_TEMPLATE, input_variables=[])
        combine_prompt = PromptTemplate(template=ANALYSIS_COMBINE_PROMPT_TEMPLATE, input_variables=[])

        chain = load_summarize_chain(
            llm,
            chain_type="map_reduce",
            map_prompt=map_prompt,
            combine_prompt=combine_prompt,
            verbose=False,
        )
        result = chain.run(docs)
        return result.strip() if isinstance(result, str) else str(result)
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