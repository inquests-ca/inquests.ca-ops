from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_sessionmaker(db_url):
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session
