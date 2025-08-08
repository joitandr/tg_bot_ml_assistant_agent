import typing as t
import logging
import os
import tempfile
import subprocess
import requests
from dotenv import load_dotenv
from datetime import datetime
import re

import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

assert os.getenv("BOT_TOKEN") is not None

# Initialize bot and dispatcher
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

SYSTEM_PROMPT = """
You are a machine learning course assistant. Your persona is that of a friendly, encouraging, and expert tutor.
Your core tasks are:

Explain complex machine learning concepts in simple terms.

Answer questions related to data science, data analysis, and statistics.

Provide relevant examples to illustrate topics.

You must follow these constraints:
Only answer questions within the defined topics.

If a question is off-topic, politely decline and offer to help with a machine learning-related question instead.

Be concise but thorough. Avoid overly long or conversational answers.
"""


@dp.message(Command('start'))
async def send_welcome(message: Message):
    await message.reply(
        """
        This is a LLM-based bot that will answer your ML-related questions
        """
    )

@dp.message(Command('help'))
async def send_help(message: Message):
    help_text = (
        "Available commands:\n\n"
        "🔹 /start - Start the bot\n"
        "🔹 /help - Show this help message\n"
    )
    await message.answer(help_text, parse_mode=ParseMode.HTML)


BOT_USERNAME = 'MLCourseAssistantBot'

@dp.message(lambda message: message.text and f"@{BOT_USERNAME}" in message.text)
async def request_to_llm(message: Message):
    user_request = message.text

    await message.reply(text="Думаю...")

    url = "https://antoncio-general-agent.hf.space/generate/openai/gpt-3.5-turbo"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "prompt": user_request,
        "max_tokens": 3_000,
        "system_prompt": SYSTEM_PROMPT,
    }

    response = requests.post(url, json=data, headers=headers)


    await message.reply(
        text=response.text
    )


async def main():
    while True:
        try:
            # Set up commands for the bot menu
            await bot.set_my_commands([
                types.BotCommand(command="start", description="Start the bot"),
                types.BotCommand(command="help", description="Show available commands"),
            ])
            
            # Start polling with retry on connection errors
            await asyncio.gather(
                dp.start_polling(bot, polling_timeout=30),
            )
        except Exception as e:
            logging.error(f"Connection error: {e}")
            logging.info("Retrying in 5 seconds...")
            await asyncio.sleep(5)
            continue

# Run the bot
if __name__ == '__main__':
    asyncio.run(main())
