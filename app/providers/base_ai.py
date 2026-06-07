from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from app.schemas.analysis import AnalysisResult

class SkinAnalyzer(ABC):
    @abstractmethod
    async def analyze(self, image_bytes: bytes, mime_type: str) -> AnalysisResult:
        pass
