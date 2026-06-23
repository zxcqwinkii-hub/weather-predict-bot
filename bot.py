import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import settings
from database.db_requests import init_db, get_user_from_db, save_user_to_db
from services.weather_api import get_weather_by_city
from services.llm_api import get_outfit_advice
from states.states import OnboardingStates   # ← ВОТ ЭТА СТРОКА ОБЯЗАТЕЛЬНА!
# Импорты наших сервисов и БД...

dp = Dispatcher()

# 1. Команда /start
@dp.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext):
    # Проверяем в БД, есть ли юзер. Если нет - начинаем онбординг
    user = await get_user_from_db(message.from_user.id)
    if not user or not user.is_onboarded:
        await message.answer("Привет! Я твой AI-стилист 🧥\nЧтобы я мог давать точные советы, напиши свой город:")
        await state.set_state(OnboardingStates.waiting_for_city)
    else:
        await message.answer("С возвращением! Нажми /outfit, чтобы узнать, как одеться сегодня.")

# 2. Обработка города
@dp.message(OnboardingStates.waiting_for_city)
async def process_city(message: Message, state: FSMContext):
    city = message.text
    # Можно тут же проверить, существует ли город через weather_api, но для MVP просто сохраняем
    await state.update_data(city=city)
    await message.answer(f"Отлично, {city}! А теперь расскажи, как ты одеваешься? (Например: 'люблю кэжуал, но ненавижу, когда потеет спина' или 'ношу только классику')")
    await state.set_state(OnboardingStates.waiting_for_style)

# 3. Обработка стиля и сохранение в БД
@dp.message(OnboardingStates.waiting_for_style)
async def process_style(message: Message, state: FSMContext):
    """Обработка ввода стиля и сохранение в БД"""
    style = message.text.strip()
    data = await state.get_data()
    
    # Сохраняем в БД
    await save_user_to_db(
        telegram_id=message.from_user.id,
        city=data['city'],
        style=style,
        is_onboarded=True
    )
    await state.clear()
    
    await message.answer(
        "Готово! 🎉\n\n"
        f"Я запомнил:\n"
        f"🏙️ Город: {data['city']}\n"
        f"👔 Стиль: {style}\n\n"
        f"Теперь напиши /outfit, когда будешь готов собраться на улицу!"
    )
# 4. Главная команда /outfit
@dp.message(Command('outfit'))
async def cmd_outfit(message: Message):
    user = await get_user_from_db(message.from_user.id)
    if not user:
        return await message.answer("Сначала пройди /start")

    await message.answer("Анализирую погоду и твой стиль... 🧠☔️")
    
    # 1. Берем погоду
    weather = await get_weather_by_city(user.city)
    if not weather:
        return await message.answer("Не могу найти такой город. Напиши /settings, чтобы изменить.")
        
    # 2. Отправляем в ИИ
    advice = await get_outfit_advice(weather, user.style)
    
    # 3. Отдаем пользователю
    await message.answer(advice)

async def main():
    bot = Bot(token=settings.telegram_bot_token)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())