import logging
import os

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

#sql server baglanti adresi(docker ortami icin optimize)
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mssql+pyodbc://sa:Asya%402026Sql@127.0.0.1:1433/OBS_System?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes&Connection+Timeout=5",
)

#db motoru olusturuluyor
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
) #db ile python arasinda boru hatti

#session factory(db oturum fabrikasi)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#modellerin turetilecegi temel sinif
Base = declarative_base()


def _create_database_if_missing() -> bool:
    """Hedef SQL Server veritabanini yoksa olusturur."""
    try:
        url = make_url(SQLALCHEMY_DATABASE_URL)
        database_name = url.database
        if not database_name:
            return False

        admin_engine = create_engine(
            url.set(database="master"),
            pool_pre_ping=True,
        )
        safe_db_name = database_name.replace("]", "]]")

        with admin_engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
            db_exists = connection.execute(
                text("SELECT DB_ID(:db_name)"),
                {"db_name": database_name},
            ).scalar()
            if db_exists is None:
                connection.execute(text(f"CREATE DATABASE [{safe_db_name}]"))

        admin_engine.dispose()
        return True
    except SQLAlchemyError as exc:
        logger.warning("Veritabani otomatik olusturulamadi: %s", exc)
        return False


def init_db(base_metadata) -> bool:
    """Tablolari olusturur. Baglanti yoksa uygulamayi dusurmez."""
    try:
        base_metadata.create_all(bind=engine)
        return True
    except SQLAlchemyError as exc:
        logger.warning("Veritabani baslatma hatasi: %s", exc)

    if _create_database_if_missing():
        try:
            base_metadata.create_all(bind=engine)
            return True
        except SQLAlchemyError as exc:
            logger.warning("Veritabani ikinci denemede de acilamadi: %s", exc)

    return False


def is_db_connected() -> bool:
    """Basit bir sorgu ile DB baglantisini test eder."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False

#DB baglantisini yoneten ve her istek sonunda kapatan fonksiyon
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() #oturumu kapatmak performans icin önemli