import json
from app.schemas.analysis import AnalysisResult, ZoneObservation, ZoneBreakdown

zones = ZoneBreakdown(
    t_zone=ZoneObservation(observations=["pores"], severity="MODERATE"),
    under_eye=ZoneObservation(observations=["dark circles"], severity="MILD")
)
result = AnalysisResult(
    image_quality="good",
    zones=zones
)

score = 100
for zone, observation in result.zones.model_dump().items():
    if not observation:
        continue
    severity = observation.get("severity", "").lower()
    print(f"Zone: {zone}, Severity: {severity}")
    if severity == "severe":
        score -= 15
    elif severity == "moderate":
        score -= 8
    elif severity == "mild":
        score -= 3
print(f"Score: {score}")
