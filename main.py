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
        
        # Let's start with admin commands
        if message.content.strip() == '!killswitch' and message.author.id == Settings.OWNER:
            # Kill the bot
            print("Killed bot.")
            exit()
        elif message.content.strip() == '!list' and message.author.id == Settings.OWNER:
            # Kill the bot
            await self.do_list_guilds(message.channel)
        elif message.content.startswith('!bail') and message.author.id == Settings.OWNER:
            # Param
            param = message.content[len("!bail "):].strip()
            
            # Bail from a guild
            await self.do_bail_out(int(param), message.channel)
        elif message.content.startswith('!thread'):
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

    async def do_list_guilds(self, channel: discord.TextChannel):
        """
        To list the guilds the bot is in!

        Args:
            channel (discord.TextChannel): The channel to send the message to
        """
        guilds_str: str = "This bot is connected to " + str(len(self.guilds)) + " servers: \n"
        async for guild in self.fetch_guilds(limit=150):
            guilds_str += guild.name + " (" + str(guild.id) + ")\n"
        await self.send_message(guilds_str, channel)

    async def do_bail_out(self, server_id: int, channel: discord.TextChannel):
        """
        To bail out the bot from servers!

        Args:
            server_id (int): The ID of the server to leave
            channel (discord.TextChannel): The channel to send the message to
        """

        guild_id: int = int(server_id)
        guild: discord.Guild = self.get_guild(guild_id)
        try: 
            print(f"Bailing from {guild.name}")
            await guild.leave()
            await self.send_message("Successfully left ", channel)
        except:
            print(f"Guild does not exist! ID: {guild_id}")
            await self.send_message(f"Guild does not exist! ID: {guild_id}", channel)
    
    async def send_message(self, message: str, channel: discord.TextChannel, split: int = 2000):
        """
        Sends a message to a channel, splitting it if it's a certain number of characters!

        Args:
            message (str): The message to send
            channel (discord.TextChannel): The channel to send the message to
            split (int, optional): The number of characters to split at. Defaults to 2000.
        """

        # If the message is over 2000 characters, split the first part, recurse the rest
        if len(message) > 2000:
            await self.send_message(message[:2000], channel)
            await self.send_message(message[2000:], channel)
        else:
            await channel.send(message)

    async def process_message(self, message: discord.Message = None, channel: discord.TextChannel = None) -> None:
        """
        Processes a message, either from a channel or a message, to respond

        Args:
            message (discord.Message, optional): The message to process. Defaults to None.
            channel (discord.TextChannel, optional): The channel to process. Defaults to None.
        """

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
