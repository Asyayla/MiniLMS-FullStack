import logging
import os

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

# SQL Server fallback string (optimized natively for containerized Docker environments)
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mssql+pyodbc://sa:Asya%402026Sql@127.0.0.1:1433/OBS_System?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes&Connection+Timeout=5",
)

# Initialize the core SQLAlchemy database connection engine with connection health checks
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
)

# Session factory for generating independent database session transaction frames
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class mapping declaration archetype for data models definitions
Base = declarative_base()


def _create_database_if_missing() -> bool:
    """
    Connects securely to the database engine using administrative fallback master frames 
    to dynamically initialize the target structural schema if it does not yet exist.
    """
    try:
        url = make_url(SQLALCHEMY_DATABASE_URL)
        database_name = url.database
        if not database_name:
            return False

        # Build independent master catalog mapping engine configuration framework
        admin_engine = create_engine(
            url.set(database="master"),
            pool_pre_ping=True,
        )
        safe_db_name = database_name.replace("]", "]]")

        # Execute check flags inside an explicit AUTOCOMMIT transaction block framework
        with admin_engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
            db_exists = connection.execute(
                text("SELECT DB_ID(:db_name)"),
                {"db_name": database_name},
            ).scalar()
            
            # Conditionally provision the target relational database infrastructure context
            if db_exists is None:
                connection.execute(text(f"CREATE DATABASE [{safe_db_name}]"))

        admin_engine.dispose()
        return True
    except SQLAlchemyError as exc:
        logger.warning("Database automation provisioning step failed: %s", exc)
        return False


def init_db(base_metadata) -> bool:
    """
    Compiles structural schema boundaries inside the targeted relational platform layout. 
    Guards against throwing fatal runtime application failure flags if connection drops.
    """
    try:
        base_metadata.create_all(bind=engine)
        return True
    except SQLAlchemyError as exc:
        logger.warning("Initial database initialization routing catch flag: %s", exc)

    # Attempt automatic provisioning fallback logic flow if tables initialization fails
    if _create_database_if_missing():
        try:
            base_metadata.create_all(bind=engine)
            return True
        except SQLAlchemyError as exc:
            logger.warning("Database instantiation path failed on retry step: %s", exc)

    return False


def is_db_connected() -> bool:
    """
    Executes a short raw test heartbeat signal query to evaluate connection health indicators.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False


def get_db():
    """
    Yields a standard secure transactional session frame context for tracking operational requests, 
    ensuring deterministic state lifecycle closure on context termination.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()