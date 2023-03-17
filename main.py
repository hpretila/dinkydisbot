import sqlite3
import discord
import copy

from discord.ext import commands

from bot_settings import Settings
from channel_manager import ChannelManager
from chat_log import MessageLog

class DinkyDisBot(discord.Client):
    def __init__(self, backend, **kwargs):
        super().__init__(**kwargs)
        self.backend = backend
        self.db_conn: sqlite3.Connection = sqlite3.connect('threads.db')
        self.thread_manager: ChannelManager = ChannelManager(self.db_conn)
    
    async def on_ready(self):
        print(f'Logged in as {self.user.name} ({self.user.id})')
    
    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.user:
            return

        if message.content.startswith('!thread'):
            async with message.channel.typing():
                # Param
                param = message.content[len("!thread"):].strip()

                # Create a new thread
                new_thread_name: str = message.author.name + "'s thread: " + param if param.strip() != "" else message.author.name + "'s thread"
                new_thread: discord.TextChannel = await message.create_thread(
                    name=new_thread_name,
                )
                await new_thread.send(f"New thread created by {message.author.mention}")
                self.thread_manager.add_thread_to_database(new_thread.id, message.author.display_name)
        elif message.content.startswith('!chat'):
            async with message.channel.typing():
                # Param
                param = message.content[len("!chat"):].strip()

                # Create a new MessageLog with just this message
                message_log: MessageLog = MessageLog()
                message_log.add_message(message.author.name, param)

                # Get the response
                response: str = self.backend.get_response(message_log=message_log, bot_name=self.user.name)

                # Log the response using logging library
                print(f"Response: {response}")

                # Send the response
            await self.send_message(response, channel)

        elif message.content.startswith('!continue'):
            # Get the channel, preserve it
            channel: discord.TextChannel = copy.deepcopy(message.channel)

            # Add this channel to the database if it isn't already
            if not self.thread_manager.is_channel_id_in_database(channel.id):
                self.thread_manager.add_thread_to_database(channel.id, message.author.display_name)

            # delete the message
            try:
                await message.delete()
            except discord.errors.Forbidden:
                print("No delete perms, seethe. :^)")

            async with message.channel.typing():
                # Process message from existing thread or TextChannel
                await self.process_message(channel=channel)

        elif self.thread_manager.is_channel_id_in_database(message.channel.id):
            # Process message from existing thread or TextChannel
            await self.process_message(message)
    
    async def send_message(self, message: str, channel: discord.TextChannel):
        # If the message is over 2000 characters, split the first part, recurse the rest
        if len(message) > 2000:
            await self.send_message(message[:2000], channel)
            await self.send_message(message[2000:], channel)
        else:
            await channel.send(message)

    async def process_message(self, message: discord.Message = None, channel: discord.TextChannel = None) -> None:
        # Get the message log of the message's channel
        if channel is None:
            channel = message.channel
            
        # Show the typing
        async with channel.typing():
            message_log: MessageLog = await self.thread_manager.generate_message_log(channel)

            # Put it through the backend
            response: str = self.backend.get_response(message_log=message_log, bot_name=self.user.name)

            # Log the response using logging library
            print(f"Response: {response}")

            # Five messages is enough; get summary!
            if (len(message_log.get_messages()) == 5):
                summary: str = self.backend.get_summary(message_log=message_log, bot_name=self.user.name)

                # Change the name if you can!
                try:
                    await message.channel.edit(name=summary)
                except:
                    print("No perms to change name, seethe. :^)")

            # Send the response
            await self.send_message(response, channel)

    
    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.user:
            return

        if message.content.startswith('!thread'):
            async with message.channel.typing():
                # Param
                param = message.content[len("!thread"):].strip()

                # Create a new thread
                new_thread_name: str = message.author.name + "'s thread: " + param if param.strip() != "" else message.author.name + "'s thread"
                new_thread: discord.TextChannel = await message.create_thread(
                    name=new_thread_name,
                )
                await new_thread.send(f"New thread created by {message.author.mention}")
                self.thread_manager.add_thread_to_database(new_thread.id, message.author.display_name)
        elif message.content.startswith('!chat'):
            async with message.channel.typing():
                # Param
                param = message.content[len("!chat"):].strip()

                # Create a new MessageLog with just this message
                message_log: MessageLog = MessageLog()
                message_log.add_message(message.author.name, param)

                # Get the response
                response: str = self.backend.get_response(message_log=message_log, bot_name=self.user.name)

                # Log the response using logging library
                print(f"Response: {response}")

                # Send the response
                await self.send_message(response, channel)

        elif message.content.startswith('!continue'):
            # Get the channel, preserve it
            channel: discord.TextChannel = self.get_channel(message.channel.id)

            # Add this channel to the database if it isn't already
            if not self.thread_manager.is_channel_id_in_database(channel.id):
                self.thread_manager.add_thread_to_database(channel.id, message.author.display_name)

            # delete the message
            try:
                await message.delete()
            except discord.errors.Forbidden:
                print("No delete perms, seethe. :^)")

            async with message.channel.typing():
                # Process message from existing thread or TextChannel
                await self.process_message(channel=channel)

        elif self.thread_manager.is_channel_id_in_database(message.channel.id):
            # Process message from existing thread or TextChannel
            await self.process_message(message)
    
def run_bot():
    # defines permissions
    intents = discord.Intents.default()
    intents.guilds = True
    intents.members = True
    intents.voice_states = True
    intents.messages = True
    intents.message_content = True

    # Create the backend
    backend = Settings.BACKEND(settings=Settings)

    # creates the bot
    client = DinkyDisBot(backend=backend, intents=intents)

    # Run the bot
    client.run(token=Settings.DISCORD_TOKEN)

if __name__ == '__main__':
    run_bot()
