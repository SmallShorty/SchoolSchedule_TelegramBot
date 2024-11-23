import asyncio
import logging
import sys
import os
import json
from datetime import datetime
from os import getenv
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from utils import load_data

# Загрузка переменных окружения
load_dotenv()
TOKEN = getenv("BOT_TOKEN")

# Файл для хранения пользовательских предпочтений
USER_PREFERENCES_FILE = "user_preferences.json"

# Инициализация Dispatcher
dp = Dispatcher()


# Загрузка пользовательских предпочтений
def load_user_preferences():
    if os.path.exists(USER_PREFERENCES_FILE):
        try:
            with open(USER_PREFERENCES_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError:
            print("Ошибка: файл с пользовательскими предпочтениями поврежден. Создается новый.")
            return {}
    return {}


# Сохранение пользовательских предпочтений
def save_user_preferences(preferences):
    with open(USER_PREFERENCES_FILE, "w", encoding="utf-8") as file:
        json.dump(preferences, file, indent=4, ensure_ascii=False)


# Глобальная переменная для хранения предпочтений пользователей
user_preferences = load_user_preferences()


# Команда /start
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Бот успешно запущен! Используйте команду /setclass, чтобы установить свой класс.")


# Команда /setclass для установки класса
@dp.message(Command("setclass"))
async def set_user_class(message: Message):
    try:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.reply("Пожалуйста, укажите класс. Например: /setclass classA")
            return

        selected_class = args[1].strip()
        # Загружаем данные, чтобы проверить существование класса
        data = load_data("data/EXAMPLE schedule.json")

        if selected_class not in data["classes"]:
            await message.reply(f"Класс '{selected_class}' не найден. Проверьте правильность ввода.")
            return

        # Сохраняем выбор пользователя
        user_preferences[message.from_user.id] = selected_class
        save_user_preferences(user_preferences)  # Сохраняем изменения в файл
        await message.reply(f"Класс успешно установлен: {selected_class}")
    except Exception as e:
        await message.reply(f"Произошла ошибка: {str(e)}")


# Команда /today для расписания на текущий день
@dp.message(Command("today"))
async def send_today_schedule(message: Message):
    try:
        # Проверяем, выбрал ли пользователь класс
        user_id = message.from_user.id
        if user_id not in user_preferences:
            await message.reply("Вы не выбрали класс. Используйте команду /setclass, чтобы установить ваш класс.")
            return

        selected_class = user_preferences[user_id]

        # Загружаем расписание
        data = load_data("data/EXAMPLE schedule.json")

        if selected_class not in data["classes"]:
            await message.reply(f"Класс '{selected_class}' больше не доступен. Пожалуйста, выберите другой класс.")
            return

        # Получаем текущий день недели
        today = datetime.now().strftime("%A")
        schedule = data["classes"][selected_class]["schedule"].get(today)

        if not schedule:
            await message.reply(f"Сегодня для класса '{selected_class}' занятий нет!")
            return

        response = f"Расписание на сегодня ({today}) для класса '{selected_class}':\n\n"

        # Формируем расписание
        for event in schedule:
            response += (f"{event['time']} - {event['subject']} "
                         f"(Преподаватель: {event['teacher']}, Аудитория: {event['room']})\n")

        await message.reply(response)
    except FileNotFoundError:
        await message.reply("Ошибка: файл с расписанием не найден.")
    except KeyError:
        await message.reply("Ошибка: структура данных расписания некорректна.")
    except Exception as e:
        await message.reply(f"Произошла ошибка: {str(e)}")


# Команда /myclass для проверки текущего установленного класса
@dp.message(Command("myclass"))
async def get_user_class(message: Message):
    user_id = message.from_user.id
    if user_id not in user_preferences:
        await message.reply("Вы еще не выбрали класс. Используйте команду /setclass, чтобы установить ваш класс.")
    else:
        await message.reply(f"Ваш установленный класс: {user_preferences[user_id]}")


# Основная функция
async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    print(f"TOKEN: {TOKEN}")
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
