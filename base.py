# base.py (Был gateways/base.py)

from abc import ABC, abstractmethod


class BaseGateway(ABC):
    """Абстрактный класс (шаблон) для всех мессенджеров."""

    def __init__(self, platform_name: str):
        self.platform = platform_name

    @abstractmethod
    async def run(self):
        """Запускает прослушивание сообщений мессенджера."""
        pass

    @abstractmethod
    async def send_message(self, user_id: str, text: str):
        """Отправляет сообщение конкретному пользователю мессенджера."""
        pass
