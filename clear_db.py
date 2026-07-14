from app.db.session import SessionLocal
from app.models.user import User
from app.models.analysis import Analysis
from app.models.analytics import AnalyticsEvent

try:
    db = SessionLocal()
    db.query(Analysis).delete()
    db.query(AnalyticsEvent).delete()
    db.query(User).delete()
    db.commit()
    print("Database cleared successfully!")
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
