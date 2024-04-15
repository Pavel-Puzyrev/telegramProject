from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

db_url = str(settings.sqlalchemy_db_url)

# engine = create_engine('postgresql://user:psw@localhost/postgres', echo=True)
engine = create_engine(db_url, pool_pre_ping=True)
session_maker = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)
