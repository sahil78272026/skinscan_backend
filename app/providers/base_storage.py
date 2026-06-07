from abc import ABC, abstractmethod
from typing import Optional

class StorageService(ABC):
    @abstractmethod
    async def upload(self, file_bytes: bytes, object_name: str, content_type: str) -> str:
        pass

    @abstractmethod
    async def delete(self, object_name: str) -> bool:
        pass

    @abstractmethod
    async def signed_url(self, object_name: str) -> Optional[str]:
        pass
