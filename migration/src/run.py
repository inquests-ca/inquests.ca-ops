import sys
from collections import defaultdict

import sqlalchemy
from openpyxl import load_workbook

from db.session import get_sessionmaker
from db.models import *


class Migrator:

    _AUTHORITY_TYPE_AUTHORITY = 'Authority'
    _AUTHORITY_TYPE_INQUEST = 'Inquest/Fatality Inquiry'

    def __init__(self, data_path, db_url):
        self._data_path = data_path
        self._session_maker = get_sessionmaker(db_url)

        # Mappings from input data IDs to new IDs.
        self._mapping_source_id = {}
        self._mapping_keyword_id = {}
        self._mapping_document_id = {}
        self._mapping_authority_id = {}

        # Maps authority IDs from input data to tuple containing authority type and source.
        self._authority_data = {}

        # Mappings of relationships between models.
        self._rel_authority_to_documents = defaultdict(list) # Uses input authority ID, new document ID.

        # These three operations must be done first to satisfy FK constraints, and are independent of each other.
        self.populate_sources()
        self.populate_keywords()
        self.populate_documents()

        # This depends on all previous operations.
        self.populate_authorities_and_inquests()

        # These two operations depend on all previous operations and are independent of each other.
        self.populate_authority_and_inquest_keywords()
        self.populate_authority_and_inquest_documents()

    def _read_worksheet(self, filename):
        """Returns iterator for rows in given Excel file."""
        wb = load_workbook('{}/{}'.format(self._data_path, filename))
        ws = wb.active

        # Start at 2nd row to ignore headers.
        return ws.iter_rows(min_row=2, values_only=True)

    def _get_db_session(self):
        """Return session object which is used to interface the database."""
        return self._session_maker()

    def _is_valid_authority_type(self, authority_type):
        return authority_type in [self._AUTHORITY_TYPE_AUTHORITY, self._AUTHORITY_TYPE_INQUEST]

    def populate_sources(self):
        # TODO: consider cleaning source data to reduce logic here.
        # TODO: consider removing code field.
        # TODO: populate rank field.
        print('[INFO] Populating sources.')

        session = self._get_db_session()

        for row in self._read_worksheet('caspio_source.xlsx'):
            rcode, rdescription = row

            source_id = None
            jurisdiction_id = None
            name = rdescription
            code = None
            rank = 0

            if rcode == 'REF':
                source_id = 'REF'
            elif rcode.startswith('UK'):
                source_id = 'UK_' + rcode[2:]
                jurisdiction_id = 'UK'
            elif rcode.startswith('US'):
                source_id = 'US_' + rcode[2:]
                jurisdiction_id = 'US'
            elif rcode == 'CANLEG':
                source_id = 'CAD_LEG'
                jurisdiction_id = 'CAD'
            elif rcode == 'FCC':
                source_id = 'CAD_FCC'
                jurisdiction_id = 'CAD'
                code = 'FCC'
            elif rcode == 'SCC':
                source_id = 'CAD_SCC'
                jurisdiction_id = 'CAD'
                code = 'SCC'
            else:
                # Assume all other sources are Canadian provinces and territories.
                source_id = 'CAD_' + rcode
                jurisdiction_id = 'CAD_' + rcode[:2]
                code = rcode

            source_id = source_id.upper()
            jurisdiction_id = jurisdiction_id.upper() if jurisdiction_id else None

            model = Source(
                sourceID=source_id,
                jurisdictionID=jurisdiction_id,
                name=name,
                code=code,
                rank=rank,
            )
            session.add(model)
            session.flush()
            self._mapping_source_id[rcode] = source_id

        session.commit()

    def populate_keywords(self):
        # TODO: populate description field or remove.
        print('[INFO] Populating keywords.')

        session = self._get_db_session()

        for row in self._read_worksheet('caspio_keywords.xlsx'):
            rtype, rkeyword, rserial = row

            if not self._is_valid_authority_type(rtype):
                print('[WARNING] Unknown authority type: {}'.format(rtype))
                continue

            # Get keyword ID from keyword name (e.g., Cause-Fall from height -> CAUSE_FALL_FROM_HEIGHT).
            keyword_id = rkeyword.upper().replace('-', '_').replace(' ', '_')

            if rtype == self._AUTHORITY_TYPE_AUTHORITY:
                model = AuthorityKeyword(
                    authorityKeywordID=keyword_id,
                    name=rkeyword,
                    description=None,
                )
            elif rtype == self._AUTHORITY_TYPE_INQUEST:
                model = InquestKeyword(
                    inquestKeywordID=keyword_id,
                    name=rkeyword,
                    description=None,
                )

            session.add(model)
            session.flush()

            self._mapping_keyword_id[rkeyword] = keyword_id

        session.commit()

    def populate_documents(self):
        print('[INFO] Populating documents.')

        session = self._get_db_session()

        for row in self._read_worksheet('caspio_docs.xlsx'):
            rauthorities, rserial, rshortname, rcitation, rdate, rlink, rlinktype = row

            model = Document(
                name=rshortname,
                date=rdate,
                link=rlink,
            )
            session.add(model)
            session.flush()

            self._mapping_document_id[rserial] = model.documentID
            for authority in rauthorities.split('\n'):
                if authority == '':
                    continue
                self._rel_authority_to_documents[authority].append(model.documentID)

        session.commit()

    def populate_authorities_and_inquests(self):
        # TODO: populate inquestID field of Authority model.
        # TODO: populate primary field of AuthorityDocuments, InquestDocuments models.
        # TODO: consider moving sourceID field to documents, despite normalization issues.
        print('[INFO] Populating authorities and inquests.')

        session = self._get_db_session()

        for row in self._read_worksheet('caspio_authorities.xlsx'):
            rserial = row[0]
            rname = row[1]
            rtype = row[3]
            rsynopsis = row[4]
            rprimary = row[9]
            rsource = row[16]
            (rlastname, rgivenname, rage, rdatedeath, rdeathcause) = row[25:30]

            if not self._is_valid_authority_type(rtype):
                print('[WARNING] Unknown authority type: {}'.format(rtype))
                continue

            self._authority_data[rserial] = (rtype, rsource)

            if rtype == self._AUTHORITY_TYPE_AUTHORITY:
                authority = Authority(
                    inquestID=None,
                    name=rname,
                    description=rsynopsis,
                    primary=rprimary
                )
                session.add(authority)
                session.flush()
                authority_id = authority.authorityID
            elif rtype == self._AUTHORITY_TYPE_INQUEST:
                # Some inquests have their name prefixed with 'Inquest-'; this is redundant.
                if rname.startswith('Inquest-'):
                    rname = rname[8:]
                inquest = Inquest(
                    sourceID=self._mapping_source_id[rsource],
                    name=rname,
                    description=rsynopsis,
                    primary=rprimary
                )
                session.add(inquest)
                session.flush()
                authority_id = inquest.inquestID

                deceased = Deceased(
                    inquestID=inquest.inquestID,
                    lastName=rlastname.title(),
                    givenNames=rgivenname.title(),
                    age=rage,
                    dateOfDeath=rdatedeath,
                    causeOfDeath=rdeathcause,
                )
                session.add(deceased)
                session.flush()

            self._mapping_authority_id[rserial] = authority_id

        session.commit()

    def populate_authority_and_inquest_keywords(self):
        print('[INFO] Populating authority and inquest keywords.')

        session = self._get_db_session()

        for row in self._read_worksheet('caspio_authorities.xlsx'):
            rserial = row[0]
            rtype = row[3]
            rkeywords = row[5]

            if not self._is_valid_authority_type(rtype):
                print('[WARNING] Unknown authority type: {}'.format(rtype))
                continue

            for keyword in rkeywords.split(','):
                if keyword == '':
                    continue

                # Ignore references to keywords which do not exist.
                if keyword not in self._mapping_keyword_id:
                    print(
                         '[WARNING] Invalid keyword {} referenced by authority with ID: {}'
                        .format(keyword, self._mapping_authority_id[rserial])
                    )
                    continue

                if rtype == self._AUTHORITY_TYPE_AUTHORITY:
                    model = AuthorityKeywords(
                        authorityID=self._mapping_authority_id[rserial],
                        authorityKeywordID=self._mapping_keyword_id[keyword],
                    )
                elif rtype == self._AUTHORITY_TYPE_INQUEST:
                    model = InquestKeywords(
                        inquestID=self._mapping_authority_id[rserial],
                        inquestKeywordID=self._mapping_keyword_id[keyword],
                    )

                # We must handle invalid FK constraints since they're not enforced in the current data structure
                # (e.g., an authority referencing an inquest keyword).
                try:
                    session.add(model)
                    session.flush()
                except sqlalchemy.exc.IntegrityError as e:
                    print(
                         '[WARNING] Integrity error for keyword {} referenced by authority with ID: {}'
                        .format(self._mapping_keyword_id[keyword], self._mapping_authority_id[rserial])
                    )
                    session.rollback()
                    continue

            # Commit for each authority since a rollback may occur at any time.
            session.commit()

    def populate_authority_and_inquest_documents(self):
        print('[INFO] Populating authority and inquest documents.')

        session = self._get_db_session()

        for authority, document_ids in self._rel_authority_to_documents.items():
            for document_id in document_ids:
                # Ignore references to authorities which do not exist.
                if authority not in self._authority_data:
                    print(
                         '[WARNING] Invalid authority {} referenced by document with ID: {}'
                        .format(authority, document_id)
                    )
                    continue

                authority_type, authority_source = self._authority_data[authority]

                if authority_type == self._AUTHORITY_TYPE_AUTHORITY:
                    model = AuthorityDocuments(
                        authorityID=self._mapping_authority_id[authority],
                        documentID=document_id,
                        sourceID=self._mapping_source_id[authority_source],
                        primary=0,
                    )
                elif authority_type == self._AUTHORITY_TYPE_INQUEST:
                    model = InquestDocuments(
                        inquestID=self._mapping_authority_id[authority],
                        documentID=document_id,
                        primary=0,
                    )

                session.add(model)
                session.flush()

        session.commit()


if __name__ == '__main__':
    data_path = sys.argv[1]
    db_url = sys.argv[2]
    Migrator(data_path, db_url)
