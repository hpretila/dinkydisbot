import discord

# Represent the chat log as a set of messages
class Message:
    def __init__ (self, author: str, msg: str) -> None:
        self.author: str = author
        self.msg: str = msg

# Represent the chat log
class MessageLog:
    def __init__(self, limit: int | None = None) -> None:
        self.messages: list[Message] = []
        self.limit: int | None = limit
    
    def add_message(self, author: str, msg: str, prepend: bool = False) -> None:
        if prepend:
            self.messages.insert(0, Message(author, msg))
        else:
            self.messages.append(Message(author, msg))

    async def add_channel(self, channel: discord.TextChannel) -> None:
        async for message in channel.history(limit=self.limit):
            self.add_message(message.author.name, message.content, prepend=True)

    def get_messages(self) -> list[Message]:
        return self.messages
    
    def to_chat_ml(self) -> list[dict[str, str]]:
        message_list = []
        for message in self.messages:
            message_list.append({"role": "user", "content": f"{message.author}:{message.msg}"})
        return message_list
    
    def __str__(self) -> str:
        res: str = ""
        for message in self.messages:
            res += f"{message.author}: {message.msg}\n"
        return res