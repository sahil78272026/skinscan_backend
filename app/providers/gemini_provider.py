import json
from google import genai
from google.genai import types
from app.providers.base_ai import SkinAnalyzer
from app.schemas.analysis import AnalysisResult
from app.config import settings
from app.providers.gemini_prompt import GEMINI_SYSTEM_PROMPT

class GeminiAnalyzer(SkinAnalyzer):
    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_api_key)
        
    async def analyze(self, image_bytes: bytes, mime_type: str) -> AnalysisResult:
        try:
            return self._call_model(settings.gemini_model, image_bytes, mime_type)
        except Exception as e:
            error_str = str(e)
            if "503" in error_str or "429" in error_str or "UNAVAILABLE" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                fallback_model = "gemini-1.5-flash-latest"
                import logging
                logger = logging.getLogger("skinscan")
                logger.warning(f"Primary model {settings.gemini_model} failed: {error_str}. Falling back to {fallback_model}.")
                return self._call_model(fallback_model, image_bytes, mime_type)
            raise e

    def _call_model(self, model_name: str, image_bytes: bytes, mime_type: str) -> AnalysisResult:
        response = self.client.models.generate_content(
            model=model_name,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                GEMINI_SYSTEM_PROMPT
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.3
            )
        )
        
        result_dict = json.loads(response.text)
        return AnalysisResult(**result_dict)

# class ClaudeAnalyzer(SkinAnalyzer): ...
# class OpenAIAnalyzer(SkinAnalyzer): ...
