from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Telegram
    telegram_bot_token: str
    
    # OpenRouter
    openrouter_api_key: str
    openrouter_referer: str = "https://t.me/your_bot"
    openrouter_title: str = "AI Weather Stylist"
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./bot.db"
    
    # LLM Models
    primary_llm_model: str = "google/gemma-4-31b-it:free"
    fallback_llm_model: str = "meta-llama/llama-3.3-70b:free"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()