import discord
import sqlite3

from chat_log import MessageLog

class ChannelManager:
    def __init__(self, db_conn: sqlite3.Connection):
        self.db_conn = db_conn
        self.create_threads_table()
    
    def create_threads_table(self) -> None:
        cursor = self.db_conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS threads (
                          channel_id INTEGER,
                          name TEXT
                          )''')
        self.db_conn.commit()
    
    def add_thread_to_database(self, channel_id: int, name: str) -> None:
        cursor = self.db_conn.cursor()
        cursor.execute('INSERT INTO threads (channel_id, name) VALUES (?, ?)', (channel_id, name))
        self.db_conn.commit()

    def is_channel_name_in_database(self, channel_id: int) -> bool:
        cursor = self.db_conn.cursor()
        cursor.execute('SELECT * FROM threads WHERE name = ?', (channel_id,))
        return cursor.fetchone() is not None
    
    def is_channel_id_in_database(self, channel_id: int) -> bool:
        cursor = self.db_conn.cursor()
        cursor.execute('SELECT * FROM threads WHERE channel_id = ?', (channel_id,))
        return cursor.fetchone() is not None
    
    async def generate_message_log(self, channel: discord.TextChannel, limit: int | None = None) -> MessageLog:
        message_log: MessageLog = MessageLog(limit)
        await message_log.add_channel(channel)
        return message_log
