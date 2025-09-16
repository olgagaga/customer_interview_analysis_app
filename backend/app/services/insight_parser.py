import re
from typing import List, Optional

from app.schemas.insight import Insight, AggregatedAnalysis, InsightCategory

_TAG_RE = re.compile(r"^\s*#(?P<tag>pain|feature|bug|feedback|insight)\b", re.IGNORECASE)
_QUOTED_RE = re.compile(r'"(?P<quote>[^"\\]*(?:\\.[^"\\]*)*)"')
_DASH_SEP_RE = re.compile(r"\s+[\-\u2013\u2014]\s+")


def _normalize_tag(tag: str) -> InsightCategory:
    t = tag.strip().lower()
    assert t in {"pain", "feature", "bug", "feedback", "insight"}
    return t  # type: ignore[return-value]


def _extract_emotion(text: str) -> tuple[str, Optional[str]]:
    text = text.strip()
    # Look for trailing (emotion)
    if text.endswith(")") and "(" in text:
        idx = text.rfind("(")
        if idx != -1 and idx < len(text) - 1:
            inner = text[idx + 1 : -1].strip()
            before = text[:idx].rstrip()
            if inner:
                return before, inner
    return text, None


def parse_insights(raw_text: Optional[str]) -> List[Insight]:
    if not raw_text:
        return []
    lines = [ln.strip() for ln in raw_text.splitlines()]
    insights: List[Insight] = []
    for line in lines:
        if not line or not line.lstrip().startswith("#"):
            continue
        m = _TAG_RE.match(line)
        if not m:
            continue
        tag = _normalize_tag(m.group("tag"))
        rest = line[m.end() :].strip()

        quote: Optional[str] = None
        interpretation: str = rest

        q = _QUOTED_RE.search(rest)
        if q:
            quote = q.group("quote").strip()
            after_quote = rest[q.end() :].strip()
            # Remove leading dash-type separators if present
            if after_quote.startswith("–") or after_quote.startswith("—") or after_quote.startswith("-"):
                after_quote = after_quote[1:].strip()
            if after_quote.startswith("-"):
                after_quote = after_quote[1:].strip()
            interpretation = after_quote if after_quote else ""
        else:
            interpretation = rest

        interpretation, emotion = _extract_emotion(interpretation)
        interpretation = interpretation.strip(" –—-").strip()
        if not interpretation and not quote:
            # Skip lines with no substantive content
            continue

        insights.append(
            Insight(
                category=tag, quote=quote if quote else None, interpretation=interpretation, emotion=emotion
            )
        )
    return insights


def format_insights_for_display(analysis: AggregatedAnalysis) -> str:
    output_lines: List[str] = []
    for ins in analysis.insights:
        parts: List[str] = [f"#{ins.category}"]
        if ins.quote:
            parts.append(f'"{ins.quote}"')
        if ins.interpretation:
            sep = " – " if ins.quote else " "
            parts.append(f"{sep}{ins.interpretation}")
        if ins.emotion:
            parts.append(f" ({ins.emotion})")
        if ins.source_filename:
            parts.append(f" [file: {ins.source_filename}]")
        output_lines.append("".join(parts))

    if analysis.irrelevant_files:
        output_lines.append("")
        output_lines.append("Irrelevant files (not interview transcripts or yielded no insights):")
        output_lines.append(", ".join(sorted(analysis.irrelevant_files)))

    return "\n".join(output_lines).strip() 