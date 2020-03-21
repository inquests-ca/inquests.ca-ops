import sys
from collections import defaultdict

from openpyxl import load_workbook

from db.session import get_sessionmaker
from db.models import *


# TODO: increase size limits on columns.
class Migrator:

    def __init__(self, data_source, db_url):
        self._data_source = data_source
        self._session_maker = get_sessionmaker(db_url)

        # Mappings from input data IDs to new IDs.
        self._mapping_source_id = {}
        self._mapping_authority_keyword_id = {}
        self._mapping_inquest_keyword_id = {}
        self._mapping_document_id = {}

        # Mappings of relationships between models.
        self._rel_authority_to_documents = defaultdict(list) # Uses input authority ID, new document ID.

        # These three operations must be done first to satisfy FK constraints, and are independent of each other.
        self.populate_sources()
        self.populate_keywords()
        self.populate_documents()

    def _read_worksheet(self, filename):
        """Returns iterator for rows in given Excel file."""
        wb = load_workbook('{}/{}'.format(self._data_source, filename))
        ws = wb.active

        # Start at 2nd row to ignore headers.
        return ws.iter_rows(min_row=2, values_only=True)

    def _get_db_session(self):
        return self._session_maker()

    def populate_sources(self):
        # TODO: consider cleaning source data to reduce logic here.
        # TODO: consider removing code field.
        # TODO: get ranks.
        session = self._get_db_session()

        for row in self._read_worksheet('caspio_source.xlsx'):
            rcode, rdescription = row

            source_id = None
            jurisdiction_id = None
            name = rdescription
            code = None
            rank = 0

            if rcode == "REF":
                source_id = "REF"
            elif rcode.startswith("UK"):
                source_id = "UK_" + rcode[2:]
                jurisdiction_id = "UK"
            elif rcode.startswith("US"):
                source_id = "US_" + rcode[2:]
                jurisdiction_id = "US"
            elif rcode == "CANLEG":
                source_id = "CAD_LEG"
                jurisdiction_id = "CAD"
            elif rcode == "FCC":
                source_id = "CAD_FCC"
                jurisdiction_id = "CAD"
                code = "FCC"
            elif rcode == "SCC":
                source_id = "CAD_SCC"
                jurisdiction_id = "CAD"
                code = "SCC"
            else:
                # Assume all other sources are Canadian provinces and territories.
                source_id = "CAD_" + rcode
                jurisdiction_id = "CAD_" + rcode[:2]
                code = rcode

            source_id = source_id.upper()
            jurisdiction_id = jurisdiction_id.upper() if jurisdiction_id else None

            self._mapping_source_id[rcode] = source_id
            model = Source(
                sourceID=source_id,
                jurisdictionID=jurisdiction_id,
                name=name,
                code=code,
                rank=rank,
            )
            session.add(model)
            session.flush()

        session.commit()

    def populate_keywords(self):
        # TODO: populate description field or remove.
        session = self._get_db_session()

        for row in self._read_worksheet('caspio_keywords.xlsx'):
            rtype, rkeyword, rserial = row

            # Get keyword ID from keyword name (e.g., Cause-Fall from height -> CAUSE_FALL_FROM_HEIGHT).
            keyword_id = rkeyword.upper().replace('-', '_').replace(' ', '_')

            if rtype == 'Authority':
                self._mapping_authority_keyword_id[rkeyword] = keyword_id
                model = AuthorityKeyword(
                    authorityKeywordID=keyword_id,
                    name=rkeyword,
                    description=None,
                )
            elif rtype == 'Inquest/Fatality Inquiry':
                self._mapping_inquest_keyword_id[rkeyword] = keyword_id
                model = InquestKeyword(
                    inquestKeywordID=keyword_id,
                    name=rkeyword,
                    description=None,
                )
            else:
                print("[WARNING] Unknown keyword type: {}".format(rtype))
                continue

            session.add(model)
            session.flush()

        session.commit()

    def populate_documents(self):
        session = self._get_db_session()

        processed_documents = set()

        for row in self._read_worksheet('caspio_docs.xlsx'):
            rauthority, rserial, rshortname, rcitation, rdate, rlink, rlinktype = row

            # Track IDs of documents that have already been processed to avoid duplicates, since one document could
            # potentially be referenced by multiple authorities.
            if rserial in processed_documents:
                print("[WARNING] Skipping document with duplicate ID: {}".format(rserial))
                continue

            processed_documents.add(rserial)

            model = Document(
                name=rshortname,
                date=rdate,
                link=rlink,
            )
            session.add(model)
            session.flush()

            self._mapping_document_id[rserial] = model.documentID
            self._rel_authority_to_documents[rauthority].append(model.documentID)

        session.commit()


if __name__ == '__main__':
    data_source = sys.argv[1]
    db_url = sys.argv[2]
    Migrator(data_source, db_url)
