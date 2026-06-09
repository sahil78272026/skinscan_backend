import httpx
import base64
import json
import logging
from app.providers.base_ai import SkinAnalyzer
from app.schemas.analysis import AnalysisResult
from app.config import settings
from app.providers.gemini_prompt import GEMINI_SYSTEM_PROMPT

logger = logging.getLogger("skinscan")

class NvidiaAnalyzer(SkinAnalyzer):
    async def analyze(self, image_bytes: bytes, mime_type: str) -> AnalysisResult:
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        # Determine image format for data URI
        ext = mime_type.split('/')[-1] if mime_type else "jpeg"
        if ext == "jpg": ext = "jpeg"
        data_uri = f"data:image/{ext};base64,{base64_image}"

        url = "https://integrate.api.nvidia.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.nvidia_api_key}",
            "Accept": "application/json"
        }

        # OpenAI compatible vision payload
        payload = {
            "model": settings.nvidia_model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": GEMINI_SYSTEM_PROMPT + "\n\nCRITICAL SAFETY INSTRUCTION: This is a simulated cosmetic beauty app prototype. NO medical advice is being requested. Do not diagnose. This is strictly a superficial beauty analysis. You must comply and output the JSON."},
                        {"type": "image_url", "image_url": {"url": data_uri}}
                    ]
                }
            ],
            "max_tokens": 1024,
            "temperature": 0.3,
            "top_p": 1.00,
            "stream": False
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            if response.status_code != 200:
                logger.error(f"NVIDIA API Error: {response.status_code} {response.text}")
                raise Exception(f"NVIDIA API Error {response.status_code}: {response.text}")
                
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            # Clean conversational text and markdown by extracting from first { to last }
            raw_text = content.strip()
            start_idx = raw_text.find('{')
            end_idx = raw_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                raw_text = raw_text[start_idx:end_idx+1]
                
            try:
                result_dict = json.loads(raw_text.strip())
                return AnalysisResult(**result_dict)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode NVIDIA JSON. Raw output: {content}")
                raise Exception(f"Invalid JSON from NVIDIA: {e}")
