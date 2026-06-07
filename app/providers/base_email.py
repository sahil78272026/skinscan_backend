from abc import ABC, abstractmethod
from app.schemas.analysis import AnalysisResult
from app.schemas.user import UserOut

class EmailService(ABC):
    @abstractmethod
    async def send_report(self, user: UserOut, analysis: AnalysisResult) -> bool:
        pass
