import asyncio
import logging
import sys
from os import getenv
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from utils import load_schedule

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Бот успешно запущен!")
    


@dp.message(Command('schedule'))
async def send_schedule(message: Message):
    try:
        # Загружаем расписание
        data = load_schedule('data/EXAMPLE schedule.json')

        response = "Расписание:\n"

        # Проходим по дням недели
        for day, events in data['schedule'].items():
            response += f"\n{day}:\n"  # Заголовок дня
            for event in events:
                # Формируем строку для каждого события
                response += (f"{event['time']} - {event['subject']} "
                             f"(Преподаватель: {event['teacher']}, Аудитория: {event['room']})\n")
        await message.reply(response)
    except FileNotFoundError:
        await message.reply("Ошибка: файл с расписанием не найден.")
    except KeyError:
        await message.reply("Ошибка: структура данных расписания некорректна.")
    except Exception as e:
        await message.reply(f"Произошла непредвиденная ошибка: {str(e)}")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(
        parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    print(TOKEN)
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
