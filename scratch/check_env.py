from app.core.config import get_settings
settings = get_settings()
print(f"KEY: {settings.openai_api_key.get_secret_value()}")
