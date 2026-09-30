from sqlmodel import create_engine


DATABASE_URL = "sqlite:///event_reservation.db"

engine = create_engine(
    DATABASE_URL,
    echo=True
)