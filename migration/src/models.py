from sqlalchemy import CHAR, Column, Date, String, text
from sqlalchemy.dialects.mysql import INTEGER, TINYINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Authority(Base):
    __tablename__ = 'authority'

    authorityId = Column(INTEGER(10), primary_key=True)
    isPrimary = Column(TINYINT(3), server_default=text("'0'"))
    name = Column(String(255))
    overview = Column(String(255))
    synopsis = Column(String(10000))
    quotes = Column(String(10000))
    notes = Column(String(5000))


class AuthorityCategory(Base):
    __tablename__ = 'authorityCategory'

    authorityCategoryId = Column(CHAR(100), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255))


class DocumentSource(Base):
    __tablename__ = 'documentSource'

    documentSourceId = Column(CHAR(100), primary_key=True)
    name = Column(String(255), nullable=False)
    hasPaywall = Column(TINYINT(3), server_default=text("'0'"))


class InquestCategory(Base):
    __tablename__ = 'inquestCategory'

    inquestCategoryId = Column(CHAR(100), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255))


class AuthorityCitations(Base):
    __tablename__ = 'authorityCitations'

    authorityId = Column('authorityId', INTEGER(10), primary_key=True, nullable=False)
    citedAuthorityId = Column('citedAuthorityId', INTEGER(10), primary_key=True, nullable=False)


class AuthorityKeyword(Base):
    __tablename__ = 'authorityKeyword'

    authorityKeywordId = Column(CHAR(100), primary_key=True)
    authorityCategoryId = Column(CHAR(100))
    name = Column(String(255), nullable=False)
    description = Column(String(255))


class AuthorityRelated(Base):
    __tablename__ = 'authorityRelated'

    authorityId = Column('authorityId', INTEGER(10), primary_key=True, nullable=False)
    relatedAuthorityId = Column('relatedAuthorityId', INTEGER(10), primary_key=True, nullable=False)


class AuthoritySuperceded(Base):
    __tablename__ = 'authoritySuperceded'

    authorityId = Column('authorityId', INTEGER(10), primary_key=True, nullable=False)
    supercededAuthorityId = Column('supercededAuthorityId', INTEGER(10), primary_key=True, nullable=False)


class InquestKeyword(Base):
    __tablename__ = 'inquestKeyword'

    inquestKeywordId = Column(CHAR(100), primary_key=True)
    inquestCategoryId = Column(CHAR(100))
    name = Column(String(255), nullable=False)
    description = Column(String(255))


class AuthorityKeywords(Base):
    __tablename__ = 'authorityKeywords'

    authorityId = Column('authorityId', INTEGER(10), primary_key=True, nullable=False)
    authorityKeywordId = Column('authorityKeywordId', CHAR(100), primary_key=True, nullable=False)


class Inquest(Base):
    __tablename__ = 'inquest'

    inquestId = Column(INTEGER(10), primary_key=True)
    jurisdictionId = Column(CHAR(100), nullable=False)
    isPrimary = Column(TINYINT(3), server_default=text("'0'"))
    name = Column(String(255), nullable=False)
    overview = Column(String(255))
    synopsis = Column(String(10000))
    notes = Column(String(5000))
    presidingOfficer = Column(String(255))
    start = Column(Date)
    end = Column(Date)
    sittingDays = Column(INTEGER(11))
    exhibits = Column(INTEGER(11))
    remarks = Column(String(1000))


class AuthorityDocument(Base):
    __tablename__ = 'authorityDocument'

    authorityDocumentId = Column(INTEGER(10), primary_key=True)
    authorityId = Column(INTEGER(10), nullable=False)
    authorityDocumentTypeId = Column(CHAR(100))
    sourceId = Column(CHAR(100))
    isPrimary = Column(TINYINT(4), server_default=text("'0'"))
    name = Column(String(255))
    citation = Column(String(255))
    created = Column(Date)


class AuthorityInquests(Base):
    __tablename__ = 'authorityInquests'

    authorityId = Column('authorityId', INTEGER(10), primary_key=True, nullable=False)
    inquestId = Column('inquestId', INTEGER(10), primary_key=True, nullable=False)


class Deceased(Base):
    __tablename__ = 'deceased'

    deceasedId = Column(INTEGER(10), primary_key=True)
    inquestId = Column(INTEGER(10))
    inquestTypeId = Column(CHAR(100))
    deathMannerId = Column(CHAR(100))
    deathCause = Column(String(255))
    deathDate = Column(Date)
    lastName = Column(String(255))
    givenNames = Column(String(255))
    age = Column(INTEGER(11))
    sex = Column(String(255))


class InquestDocument(Base):
    __tablename__ = 'inquestDocument'

    inquestDocumentId = Column(INTEGER(10), primary_key=True)
    inquestId = Column(INTEGER(10), nullable=False)
    inquestDocumentTypeId = Column(
        CHAR(100),
        comment='E.g., verdict, ruling, exhibit.\\nCan be NULL if document falls into misc. category.'
    )
    name = Column(String(255))
    created = Column(Date)


class InquestDocumentLinks(Base):
    __tablename__ = 'inquestDocumentLinks'

    inquestDocumentId = Column(INTEGER(10), primary_key=True)
    documentSourceId = Column(CHAR(100), primary_key=True, nullable=False)
    link = Column(String(1000), nullable=False)


class InquestKeywords(Base):
    __tablename__ = 'inquestKeywords'

    inquestId = Column('inquestId', INTEGER(10), primary_key=True, nullable=False)
    inquestKeywordId = Column('inquestKeywordId', CHAR(100), primary_key=True, nullable=False)


class AuthorityDocumentLinks(Base):
    __tablename__ = 'authorityDocumentLinks'

    authorityDocumentId = Column(INTEGER(10), primary_key=True, nullable=False)
    documentSourceId = Column(CHAR(100), primary_key=True, nullable=False)
    link = Column(String(1000), nullable=False)
