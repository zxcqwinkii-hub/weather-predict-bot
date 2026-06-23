import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# OpenRouter клиент — совместим с OpenAI SDK
client = AsyncOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "https://t.me/your_bot_username",  # Обязательно для OpenRouter
        "X-Title": "AI Weather Stylist Bot",                # Название вашего приложения
    },
)

# Основная модель и фоллбэк
PRIMARY_MODEL = "google/gemma-4-31b-it:free"
FALLBACK_MODEL = "meta-llama/llama-3.3-70b:free"

SYSTEM_PROMPT = """
Ты — заботливый AI-стилист и помощник на каждый день. 
Твоя задача: дать краткий практичный совет (3-5 предложений), как одеться и что учесть.

ПРАВИЛА:
1. Опирайся на погоду и почасовой прогноз. Если к вечеру похолодает или пойдет дождь — предупреди.
2. Учитывай предпочтения пользователя по стилю и комфорту.
3. Пиши дружелюбно, тепло, используй уместные эмодзи (не больше 3-4 на сообщение).
4. НЕ используй сложные метеорологические термины.
5. Давай конкретные советы: не "оденься теплее", а "надень худи и ветровку".
6. Если данные странные (например, пользователь написал ерунду про стиль) — мягко уточни.
"""

def _format_weather_for_llm(weather_data: dict) -> str:
    """Превращаем сырой JSON погоды в читаемый для LLM текст."""
    current = weather_data['current']
    hourly = weather_data['hourly']
    
    # Берем только ключевые часы, чтобы не жечь токены
    hours_sample = []
    for i in range(0, min(24, len(hourly['time'])), 3):
        hours_sample.append({
            "time": hourly['time'][i],
            "temp": hourly['temperature_2m'][i],
            "rain_prob": hourly['precipitation_probability'][i]
        })
    
    return f"""
Город: {weather_data['city']}
Сейчас: {current['temperature_2m']}°C, ветер {current['wind_speed_10m']} м/с, влажность {current['relative_humidity_2m']}%.
Код погоды: {current['weather_code']}

Прогноз по часам (каждые 3 часа):
{json.dumps(hours_sample, ensure_ascii=False)}
"""

async def get_outfit_advice(weather_data: dict, user_preferences: str) -> str:
    weather_summary = _format_weather_for_llm(weather_data)
    user_context = f"Предпочтения: {user_preferences or 'не указаны'}"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"{weather_summary}\n\n{user_context}\n\nДай совет на день:"}
    ]

    # Пробуем основную модель, при ошибке — фоллбэк
    for model in (PRIMARY_MODEL, FALLBACK_MODEL):
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=300,  # Экономим токены
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Model {model} failed: {e}")
            continue
    
    return "Ой, мой AI-мозг перегрелся 🥵 Попробуй через минуту!"