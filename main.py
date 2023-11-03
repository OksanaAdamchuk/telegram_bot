import asyncio
import logging
import sys
import openai
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from commands import set_commands
from database import store_idea, get_ideas


load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

TOKEN = os.getenv("TELEGRAM_API_TOKEN")

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")


# Define a command to start a conversation with AI
@dp.message(Command(commands='ask'))
async def ask_question(message: types.Message):
    # Use OpenAI to generate a question
    ai_question = generate_ai_question()
    
    # Send the AI-generated question to the user

    ai_developer_answer = generate_ai_developer_answer(ai_question)
    ai_tester_answer = generate_ai_tester_answer(ai_developer_answer)

    await message.answer(f'{hbold("Idea Generator")}. {ai_question}')
    await message.reply(f'{hbold("Developer")}. {ai_developer_answer}')
    await message.reply(f'{hbold("Tester")}. {ai_tester_answer}')


@dp.message()
async def chat_gpt(message: types.Message) -> None:
    existing_ideas = [idea["function_idea"] for idea in get_ideas()]
    # Define a system message to set the behavior or context of the assistant.
    system_message = {"role": "system", "content": f"You are a helpful assistant, that checks what functions are in the DB ({', '.join(existing_ideas)}) and if user question is about one of them answers user. But if user's question not about one of DB functions you appologies that can't provide information about something that not in the DB."}

    # Create a user message using the content of the received message.
    user_message = {"role": "user", "content": message.text}

    # Create a conversation list starting with the system message followed by the user message.
    conversation = [system_message, user_message]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
        temperature=0.8,
        max_tokens=526
    )

    assistant_response = response.choices[0].message['content']

    await message.reply(assistant_response)


def generate_ai_question():
    # Retrieve all existing ideas from the database
    existing_ideas = [idea["function_idea"] for idea in get_ideas()]

    # Create a message instructing OpenAI to analyze previous answers
    user_message = {
        "role": "user",
        "content": f"Analyze all your previous answers, that are in the DB ({', '.join(existing_ideas)}), and generate an idea of the function that is not in DB yet. Don't write code of that function."
    }

    # Use OpenAI to generate an AI question
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful creator of ideas."},
            user_message,
        ],
        temperature=0.8,
        max_tokens=128,
    )

    ai_answer = response.choices[0]['message']['content']

    # Check if the generated question already exists in the database
    if ai_answer not in existing_ideas:
        store_idea(ai_answer)
        return ai_answer

    # If the generated question already exists in the database, try again
    return generate_ai_question()


def generate_ai_developer_answer(ai_question):
    # Use OpenAI to generate an AI answer to the AI-generated question
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful developer."},
            {"role": "user", "content": f"Write Python code for suggested function: {ai_question}"},
        ],
        temperature=0.8,
        max_tokens=512,
    )
    
    return response.choices[0]['message']['content']


def generate_ai_tester_answer(ai_question):
    # Use OpenAI to generate an AI answer to the AI-generated question
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful tester."},
            {"role": "user", "content": f"Write unittest for function: {ai_question}"},
        ],
        temperature=0.8,
        max_tokens=512,
    )
    
    return response.choices[0]['message']['content']


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

    await set_commands(bot)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
