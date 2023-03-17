from chat_log import MessageLog
from bot_settings import Settings

class BaseBackend:
    def __init__(self, settings: Settings):
        self.settings: Settings = settings

    def get_response(self, message_log: MessageLog, bot_name: str) -> str:
        raise NotImplementedError("get_response(_,_) not implemented. Subclass must implement abstract method")

    def get_summary(self, message_log: MessageLog) -> str:
        raise NotImplementedError("get_summary(_,_) Subclass must implement abstract method")