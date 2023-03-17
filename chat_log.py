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
    
    def to_chat_ml(self, char_limit: None | int = None) -> list[dict[str, str]]:
        message_list = []
        cum_len = 0
        prev_author = None

        # Go through each message backwards
        for message in reversed(self.messages):
            # Add the message to the start of the list
            content: str = f"{message.author}:{message.msg}"

            # Stop adding messages if we've reached the char limit
            if char_limit is not None and cum_len + len(content) > char_limit:
                break
            else:
                # If the prev_author is the same, go select the first message in the list and prepend the content to it
                if prev_author == message.author:
                    # Remove the f"{message.author}:" from the content
                    prev_content: str = (message_list[0]["content"])[len(message.author) + 1:]

                    # Prepend the content to the previous content
                    content = f"{message.author}:{content}\n{prev_content}".strip()

                    message_list[0]["content"] = content
                else:
                    message_list.insert(0, {"role": "user", "content": content})
            
            # Set the prev_author to the current author
            prev_author = message.author

            # Add the length of the message to the cumulative length
            cum_len += len(content)

        return message_list
    
    def __str__(self) -> str:
        res: str = ""
        for message in self.messages:
            res += f"{message.author}: {message.msg}\n"
        
        return res