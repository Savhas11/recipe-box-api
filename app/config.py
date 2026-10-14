import os

class Config:
    JWT_ALGORITHM = "HS256"
    DATABASE = os.getenv("DATABASE_PATH")
    JWT_SECRET = os.getenv("JWT_SECRET")

    if not DATABASE or not JWT_SECRET:
        raise RuntimeError("Required config missing: DATABASE_PATH or JWT_SECRET")


class DevelopmentConfig(Config):
    pass


class TestingConfig(Config):
    pass


class ProductionConfig(Config):
    pass