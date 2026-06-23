import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from config import settings

# ⚠️ ВАЖНО: Импортируем ОБА - Base И User!
from database.models import Base, User

logger = logging.getLogger(__name__)

# Создаем асинхронный движок
engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    """Инициализация базы данных (создание таблиц)"""
    logger.info(f"📦 Создаю таблицы в БД: {settings.database_url}")
    logger.info(f"📋 Модели в metadata: {Base.metadata.tables.keys()}")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("✅ Таблицы БД созданы успешно!")

async def get_user_from_db(telegram_id: int) -> User | None:
    """Получить пользователя из БД"""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

async def save_user_to_db(telegram_id: int, city: str, style: str, is_onboarded: bool = False):
    """Сохранить или обновить пользователя в БД"""
    async with async_session() as session:
        user = await get_user_from_db(telegram_id)
        
        if user:
            user.city = city
            user.style = style
            user.is_onboarded = is_onboarded
        else:
            user = User(
                telegram_id=telegram_id,
                city=city,
                style=style,
                is_onboarded=is_onboarded
            )
            session.add(user)
        
        await session.commit()
        return user