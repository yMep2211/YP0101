#Модуль для подключения к базе данных PostgreSQL и создания сессий

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_URI = ("postgresql+psycopg2://postgres:Qwerasdf135#@localhost:5432/postgres?options=-csearch_path%3Dpartner_module")

# Создаём объект Engine для подключения к БД
engine = create_engine(DB_URI)

# Каждый вызов SessionLocal() создаёт новый объект Session через который выполняются все операции с БД 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Метод для использования сессий через создание
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

