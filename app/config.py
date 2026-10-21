import os
from pathlib import Path

class Config:
    JWT_ALGORITHM = "HS256"
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATABASE = BASE_DIR / os.getenv("DATABASE_PATH", "recipes.db")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE}"
    JWT_SECRET = os.getenv("JWT_SECRET")

    if not DATABASE or not JWT_SECRET:
        raise RuntimeError("Required config missing: DATABASE_PATH or JWT_SECRET")


class DevelopmentConfig(Config):
    pass


class TestingConfig(Config):
    DATABASE = "instance/test_recipes.sqlite"



class ProductionConfig(Config):
    pass