from app.db.session import SessionLocal
from app.models.analysis import Analysis
import datetime

db = SessionLocal()
analyses = db.query(Analysis).filter(Analysis.ip_address != None).all()
print(f"Total anonymous analyses: {len(analyses)}")
