from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# TODO: pull connection URL from script inputs.

def _get_sessionmaker():
    engine = create_engine('mysql+pymysql://root@127.0.0.1:3307/inquestsca')
    Session = sessionmaker(bind=engine)
    return Session

_Session = _get_sessionmaker()

def create_session():
    global _Session
    return _Session()
