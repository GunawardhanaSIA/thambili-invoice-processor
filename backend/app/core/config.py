class Settings:
    api_prefix: str = "/api"
    cors_origins: list[str] = ["http://localhost:5173"]
    database_url: str = "sqlite:///./invoice_processor.db"
    upload_dir: str = "uploads"
    ocr_dpi: int = 300


settings = Settings()
