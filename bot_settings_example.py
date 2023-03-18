from chat_backend_gpt_turbo import GPTTurboBackend

class Settings:
    DISCORD_TOKEN : int = ""
    OPENAI_API_KEY : str = ""
    BACKEND = GPTTurboBackend
    OWNER = 0
    WHITELIST = [
        0,
    ]