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
        response = self.client.models.generate_content(
            model=settings.gemini_model,
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
