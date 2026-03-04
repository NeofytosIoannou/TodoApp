from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import make_url
from .config import settings

SQLALCHEMY_DATABASE_URL = settings.database_url.strip().strip('"').strip("'")

if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
	SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

parsed_url = make_url(SQLALCHEMY_DATABASE_URL)
if parsed_url.drivername != "sqlite" and not parsed_url.host:
	raise ValueError("Invalid DATABASE_URL: host is empty. Check your Render DATABASE_URL value.")

engine_kwargs = {}
if parsed_url.drivername == "sqlite":
	engine_kwargs["connect_args"] = {"check_same_thread": False}
elif parsed_url.drivername.startswith("postgresql"):
	if "sslmode" not in parsed_url.query:
		engine_kwargs["connect_args"] = {"sslmode": settings.db_sslmode}

engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
