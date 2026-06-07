from app.schemas.analysis import AnalysisResult
import re

# Banned medical terms mapped to cosmetic equivalents
BANNED_TERMS_MAP = {
    "acne": "blemishes",
    "melasma": "uneven tone",
    "rosacea": "redness",
    "eczema": "dry patches",
    "dermatitis": "dry patches",
    "deficiency": "dullness",
    "disorder": "imbalance",
    "disease": "imbalance",
    "diagnosis": "analysis",
    "treatment": "routine",
    "cure": "improve"
}

def sanitize_text(text: str) -> str:
    if not text:
        return text
    
    sanitized = text
    for banned, cosmetic in BANNED_TERMS_MAP.items():
        # Case insensitive replacement, simplistic approach for now
        pattern = re.compile(re.escape(banned), re.IGNORECASE)
        sanitized = pattern.sub(cosmetic, sanitized)
    return sanitized

def sanitize_analysis(analysis: AnalysisResult) -> AnalysisResult:
    """
    Scans AI output and strips/maps banned medical terms to cosmetic language
    BEFORE returning to the client or persisting.
    """
    if analysis.skin_type:
        analysis.skin_type = sanitize_text(analysis.skin_type)
    if analysis.skin_tone:
        analysis.skin_tone = sanitize_text(analysis.skin_tone)
        
    if analysis.top_concerns:
        analysis.top_concerns = [sanitize_text(c) for c in analysis.top_concerns]
        
    if analysis.focus_areas:
        analysis.focus_areas = [sanitize_text(fa) for fa in analysis.focus_areas]
        
    if analysis.routine:
        if analysis.routine.morning:
            analysis.routine.morning = [sanitize_text(step) for step in analysis.routine.morning]
        if analysis.routine.evening:
            analysis.routine.evening = [sanitize_text(step) for step in analysis.routine.evening]
            
    if analysis.lifestyle_nudges:
        analysis.lifestyle_nudges = [sanitize_text(nudge) for nudge in analysis.lifestyle_nudges]
        
    if analysis.encouragement_note:
        analysis.encouragement_note = sanitize_text(analysis.encouragement_note)
        
    if analysis.zones:
        for zone_name in ["forehead", "t_zone", "left_cheek", "right_cheek", "under_eye", "chin_jawline"]:
            zone = getattr(analysis.zones, zone_name)
            if zone and zone.observations:
                zone.observations = [sanitize_text(obs) for obs in zone.observations]
                
    return analysis
