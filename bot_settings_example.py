from chat_backend import BaseBackend
from chat_backend_gpt_turbo import GPTTurboBackend

class Settings:
    DISCORD_TOKEN: int = ""
    OPENAI_API_KEY: str = ""
    BACKEND: type['BaseBackend'] = GPTTurboBackend
    OWNER = None