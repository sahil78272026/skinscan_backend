import httpx
import base64
import json
import logging
from app.providers.base_ai import SkinAnalyzer
from app.schemas.analysis import AnalysisResult
from app.config import settings
from app.providers.gemini_prompt import GEMINI_SYSTEM_PROMPT

logger = logging.getLogger("skinscan")

class OpenRouterAnalyzer(SkinAnalyzer):
    async def analyze(self, image_bytes: bytes, mime_type: str) -> AnalysisResult:
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        # Determine image format for data URI
        ext = mime_type.split('/')[-1] if mime_type else "jpeg"
        if ext == "jpg": ext = "jpeg"
        data_uri = f"data:image/{ext};base64,{base64_image}"

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "HTTP-Referer": settings.frontend_origin, 
            "X-Title": "SkinScan",
            "Accept": "application/json"
        }

        # OpenAI compatible vision payload
        payload = {
            "model": settings.openrouter_model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": GEMINI_SYSTEM_PROMPT},
                        {"type": "image_url", "image_url": {"url": data_uri}}
                    ]
                }
            ],
            # Ask OpenRouter strictly for JSON
            "response_format": {"type": "json_object"},
            "temperature": 0.3,
            "stream": False
        }

        import asyncio
        max_retries = 3
        
        async with httpx.AsyncClient(timeout=90.0) as client:
            for attempt in range(max_retries):
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code in [429, 502, 503, 504]:
                    if attempt < max_retries - 1:
                        logger.warning(f"OpenRouter rate limit/server error ({response.status_code}). Retrying in {2 ** attempt}s...")
                        await asyncio.sleep(2 ** attempt)
                        continue
                    else:
                        logger.error(f"OpenRouter API Error: {response.status_code} {response.text}")
                        raise Exception(f"OpenRouter API Error {response.status_code}: {response.text}")
                elif response.status_code != 200:
                    logger.error(f"OpenRouter API Error: {response.status_code} {response.text}")
                    raise Exception(f"OpenRouter API Error {response.status_code}: {response.text}")
                    
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                # Intercept broken model responses like "User Safety: safe"
                if "User Safety: safe" in content or "I don't feel safe" in content:
                    if attempt < max_retries - 1:
                        logger.warning(f"OpenRouter routed to a broken/over-filtered model (Raw: {content}). Retrying...")
                        await asyncio.sleep(2 ** attempt)
                        continue
                    else:
                        raise Exception(f"Failed to bypass upstream model guardrails. Raw: {content}")
                
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
                    if attempt < max_retries - 1:
                        logger.warning(f"Failed to decode OpenRouter JSON on attempt {attempt + 1}. Retrying...")
                        await asyncio.sleep(2 ** attempt)
                        continue
                    else:
                        logger.error(f"Failed to decode OpenRouter JSON permanently. Raw output: {content}")
                        raise Exception(f"Invalid JSON from OpenRouter: {e}")
