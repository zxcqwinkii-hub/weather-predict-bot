import asyncio
from database.db_requests import init_db, engine
from database.models import Base, User

async def test():
    print("🔍 Проверяю модели...")
    print(f"Модели в metadata: {Base.metadata.tables.keys()}")
    
    print("\n🔧 Создаю таблицы...")
    await init_db()
    
    print("\n✅ Готово! Проверь файл bot.db")

if __name__ == "__main__":
    asyncio.run(test())