# coding: utf-8
from sqlalchemy import CHAR, Column, Date, String, Table, text
from sqlalchemy.dialects.mysql import INTEGER, TINYINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class AuthorityKeyword(Base):
    __tablename__ = 'authorityKeyword'

    authorityKeywordID = Column(CHAR(100), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255))


class DocumentType(Base):
    __tablename__ = 'documentType'

    documentType = Column(CHAR(100), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255))


class InquestKeyword(Base):
    __tablename__ = 'inquestKeyword'

    inquestKeywordID = Column(CHAR(100), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255))


class Sovereignty(Base):
    __tablename__ = 'sovereignty'

    sovereigntyID = Column(CHAR(100), primary_key=True, comment='For a country, its ISO code.')
    sovereignty = Column(String(255), nullable=False, comment='Generally, but not always, a country')


class Document(Base):
    __tablename__ = 'document'

    documentID = Column(INTEGER(10), primary_key=True, autoincrement=True)
    name = Column(String(255))
    date = Column(Date)
    link = Column(String(1000))
    documentType = Column(CHAR(100), comment='E.g., verdict, ruling, exhibit.\\nCan be NULL if document falls into misc. category.')


class Jurisdiction(Base):
    __tablename__ = 'jurisdiction'

    jurisdictionID = Column(CHAR(100), primary_key=True, nullable=False, comment='Generally concatenation of sovereignty code and division code (e.g., CAD_ON).')
    sovereigntyID = Column(CHAR(100), primary_key=True, nullable=False, comment='Generally, but not always, a country')
    subdivision = Column(String(255), comment='Generally a province, territory, or state. \\nNULL implies this jurisdiction is federal.')
    code = Column(String(255), nullable=False)


class Source(Base):
    __tablename__ = 'source'

    sourceID = Column(CHAR(100), primary_key=True, comment='Generally concatenation of sovereignty code and court code (e.g., CAD_ONCA).')
    jurisdictionID = Column(CHAR(100))
    name = Column(String(255), nullable=False)
    code = Column(String(255))
    rank = Column(INTEGER(10), nullable=False, comment='Rank which determines the importance of the source, and whether it is binding.')


class Inquest(Base):
    __tablename__ = 'inquest'

    inquestID = Column(INTEGER(10), primary_key=True, autoincrement=True)
    sourceID = Column(CHAR(100), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(10000))
    primary = Column(TINYINT(3), server_default=text("'0'"))


class Authority(Base):
    __tablename__ = 'authority'

    authorityID = Column(INTEGER(10), primary_key=True, autoincrement=True)
    inquestID = Column(INTEGER(10))
    name = Column(String(255))
    description = Column(String(10000))
    primary = Column(TINYINT(3), server_default=text("'0'"))


class Deceased(Base):
    __tablename__ = 'deceased'

    deceasedID = Column(INTEGER(10), primary_key=True, autoincrement=True)
    inquestID = Column(INTEGER(10))
    lastName = Column(String(255))
    givenNames = Column(String(255))
    age = Column(INTEGER(11))
    dateOfDeath = Column(Date)
    causeOfDeath = Column(String(255))


class InquestDocuments(Base):
    __tablename__ = 'inquestDocuments'

    inquestID = Column(INTEGER(10), primary_key=True, nullable=False)
    documentID = Column(INTEGER(10), primary_key=True, nullable=False)
    primary = Column(TINYINT(4), server_default=text("'0'"))


class InquestKeywords(Base):
    __tablename__ = 'inquestKeywords'

    inquestID = Column('inquestID', INTEGER(10), primary_key=True, nullable=False)
    inquestKeywordID = Column('inquestKeywordID', CHAR(100), primary_key=True, nullable=False)


class AuthorityDocuments(Base):
    __tablename__ = 'authorityDocuments'

    authorityID = Column(INTEGER(10), primary_key=True, nullable=False)
    documentID = Column(INTEGER(10), primary_key=True, nullable=False)
    sourceID = Column(CHAR(100))
    primary = Column(TINYINT(4), server_default=text("'0'"))


class AuthorityKeywords(Base):
    __tablename__ = 'authorityKeywords'

    authorityID = Column('authorityID', INTEGER(10), primary_key=True, nullable=False)
    authorityKeywordID = Column('authorityKeywordID', CHAR(100), primary_key=True, nullable=False)
