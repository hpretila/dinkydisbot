# dinkydisbot
General purpose Discord bot to interact with LLMs.

## Setup 🧰
1. Install the required packages with
    ```bash
    pip install -r requirements.txt
    ```
2. Create a new `bot_settings.py` (see `bot_settings.py.example` for an example). Provide a Backend, a Discord Bot token and an OpenAI token.
3. Run the bot with
    ```bash
    python main.py
    ```

## Usage 🤖
On Discord the following commands are available:
- `!thread` to start a new thread for the bot to watch and respond to.
- `!chat` to give one-shot responses.

## Backends 🧠
The bot can be configured to use different backends. Currently, the following backends are available:
- `GPTTurboBackend`: Uses the OpenAI API to generate responses with `gpt-3.5-turbo`.

To define a backend, provide overrides for the following functions:
- `def get_response(self, message_log: MessageLog, bot_name: str) -> str:`: Returns a response to the given prompt. You are provided a message log which contains the chronological history of messages in the thread. The bot name is provided to allow the backend to filter out messages from the bot itself.
- `def get_summary(self, message_log: MessageLog) -> str:`: Returns a summary of the given message log.

## Progress 🚧
- [x] Basic chatbot functionality
- [x] Basic thread functionality
- [x] Basic backend functionality
- [x] `gpt-3.5-turbo` backend.
- [ ] `gpt-j` backend.