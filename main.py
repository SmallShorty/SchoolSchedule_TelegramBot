import asyncio
import json
import logging
import sys
from idlelib.iomenu import encoding
from os import getenv
from textwrap import indent

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from aiogram import F

from utils.useJSON import load_json
import keyboards as kb

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()

class_pref = load_json('data/class_pref.json')


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Бот успешно запущен!",
                         reply_markup = kb.start)


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

@dp.message(Command("id"))
async def get_id(message: Message):
    user_id = str(message.from_user.id)
    await message.reply(user_id)

@dp.message(Command("setclass"))
async def set_class(message: Message):
    user_id = str(message.from_user.id)
    args = message.text.split()
    if len(args) != 2:
        await message.reply("Введите класс в формате /setclass 3Б")
        return
    print(args)
    selected_class = args[1].strip()
    class_pref[user_id] = selected_class
    with open('data/class_pref.json', "w", encoding="utf-8") as file:
        json.dump(class_pref, file, indent=4, ensure_ascii=False)
    await message.reply("Класс успешно указан")

@dp.message(Command("myclass"))
async def get_class(message: Message):
    user_id = str(message.from_user.id)
    user_class = class_pref[user_id]
    await message.reply(f'Ваш класс {user_class}')

@dp.message(F.text.lower() == "расписание")
async def send_schedule(message: Message):
    try:
        user_class = class_pref[str(message.from_user.id)]
        schedule = load_json(f"data/{user_class}.json")
        print(schedule)
    except KeyError:
        await message.reply("Вы не указали свой класс. Пожалуйста, используйте команду /setclass вашкласс")
    except FileNotFoundError:
        await message.reply("Расписание для этого класса не добавили")



if __name__ == "__main__":
    print(TOKEN)
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())