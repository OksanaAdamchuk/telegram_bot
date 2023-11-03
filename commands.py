from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="the beginning of work"),
        BotCommand(
            command="ask", description="ask to generate some function and tests"
        ),
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())
