from typing import Literal, Optional, List
from pydantic import BaseModel


InsightCategory = Literal["pain", "feature", "bug", "feedback", "insight"]


class Insight(BaseModel):
    category: InsightCategory
    quote: Optional[str] = None
    interpretation: str
    emotion: Optional[str] = None
    source_filename: Optional[str] = None


class AggregatedAnalysis(BaseModel):
    insights: List[Insight]
    irrelevant_files: List[str] = [] 