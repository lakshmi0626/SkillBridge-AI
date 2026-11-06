from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "SkillBridge AI"
    database_url: str = "sqlite:///./skillbridge.db"
    secret_key: str = "CHANGE_THIS_SECRET_KEY_BEFORE_DEPLOYMENT_32_CHARS_MIN"
    access_token_minutes: int = 45
    upload_dir: str = "./storage/resumes"
    max_upload_mb: int = 8
    frontend_origin: str = "http://localhost:5173"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
