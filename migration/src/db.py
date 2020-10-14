from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DatabaseClient:

    def __init__(self, db_url):
        engine = create_engine(db_url)
        self._session_maker = sessionmaker(bind=engine)

    def get_session(self):
        return self._session_maker()
