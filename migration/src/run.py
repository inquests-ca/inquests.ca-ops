import sys
import re
from collections import defaultdict

import sqlalchemy
from openpyxl import load_workbook

from db.session import get_sessionmaker
from db.models import *


# TODO: set not-null constraint on fields consistently.

class Migrator:

    _AUTHORITY_TYPE_AUTHORITY = 'Authority'
    _AUTHORITY_TYPE_INQUEST = 'Inquest/Fatality Inquiry'

    def __init__(self, file_path, db_url):
        self._file_path = file_path
        self._session_maker = get_sessionmaker(db_url)

        # Mappings from input data IDs to new IDs.
        self._mapping_source_id = self._get_source_mappings()
        self._mapping_keyword_id = {}
        self._mapping_authority_id = {}

        # Maps authority IDs from input data to tuple containing authority type and source.
        self._authority_data = {}

        # Maps authority IDs to tuple containing related authorities and cited authorities.
        self._authority_related = {}

        # Mappings of relationships between models.
        self._rel_authority_to_primary_document = {}         # Uses input authority ID, document citation.

        # This operation must be done first to satisfy FK constraints.
        self.populate_keywords()

        # This depends on the previous operation.
        self.populate_authorities_and_inquests()

        # These operations depend on all previous operations and are independent of each other.
        self.populate_authority_relationships()
        self.populate_authority_and_inquest_keywords()
        self.populate_documents()

    def _read_worksheet(self, sheet):
        """Returns iterator for rows in given Excel file."""
        wb = load_workbook(self._file_path)
        ws = wb[sheet]

        # Start at 2nd row to ignore headers.
        return ws.iter_rows(min_row=2, values_only=True)

    def _get_db_session(self):
        """Return session object which is used to interface the database."""
        return self._session_maker()

    def _is_valid_authority_type(self, authority_type):
        return authority_type in [self._AUTHORITY_TYPE_AUTHORITY, self._AUTHORITY_TYPE_INQUEST]

    def _format_as_id(self, name):
        """Formats string to an appropriate ID."""
        return (
            name
                .upper()
                .replace('-', '_')
                .replace(' ', '_')
                .replace('.', '_')
                .replace('/', '_')
        )

    def _format_date(self, date_str):
        """Format date string into SQL-compatible date."""
        if date_str == '':
            return None
        elif re.match(r'\d{4}-\d{2}-\d{2}', date_str) is not None:
            # Date is already in valid format.
            return date_str
        else:
            match = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', date_str)
            if match is not None and len(match.groups()) == 3:
                (month, day, year) = match.groups()
                return "{}-{}-{}".format(year, month, day)
            else:
                raise ValueError("Invalid date: {}".format(date_str))

    def _get_source_mappings(self):
        # TODO: resolve duplicates with Alberta Inquest Inquiry.
        return {
            'ABCA': 'CAD_ABCA',
            'ABCQB': 'CAD_ABCQB',
            'ABFI': 'CAD_ABINQ',
            'ABINQ': 'CAD_ABINQ',
            'ABLEG': 'CAD_ABLEG',
            'BCCA': 'CAD_BCCA',
            'BCINQ': 'CAD_BCINQ',
            'BCLEG': 'CAD_BCLEG',
            'BCSC': 'CAD_BCSC',
            'FCC': 'CAD_FCC',
            'CANLEG': 'CAD_LEG',
            'MBCA': 'CAD_MBCA',
            'MBCQB': 'CAD_MBCQB',
            'NSCA': 'CAD_NSCA',
            'NUINQ': 'CAD_NUINQ',
            'ONCA': 'CAD_ONCA',
            'ONINQ': 'CAD_ONINQ',
            'ONJI': 'CAD_ONJI',
            'ONLEG': 'CAD_ONLEG',
            'ONOCC': 'CAD_ONOCC',
            'ONOLRC': 'CAD_ONOLRC',
            'ONPI': 'CAD_ONPI',
            'ONSCJ': 'CAD_ONSCJ',
            'SCC': 'CAD_SCC',
            'SKLEG': 'CAD_SKLEG',
            'SKQB': 'CAD_SKQB',
            'YKCA': 'CAD_YKCA',
            'UKSenC': 'UK_SENC',
            'USSC': 'US_SC',
            'REF': 'REF',
        }

    def populate_keywords(self):
        # TODO: populate description field.
        print('[INFO] Populating keywords.')

        session = self._get_db_session()

        authority_categories = set()
        inquest_categories = set()

        for row in self._read_worksheet('KeywordsLookup'):
            rtype, rkeyword, _, rserial = row

            if not self._is_valid_authority_type(rtype):
                print('[WARNING] Unknown authority type: {}'.format(rtype))
                continue

            # Most keywords are prefixed by categories (e.g., Cause-Fall from height -> Cause).
            # Otherwise, use 'General' as the default category.
            if '-' in rkeyword:
                category = (rkeyword.split('-', 1)[0])
            else:
                category = 'General'

            # Create category if it does not exist.
            category_id = self._format_as_id(category)
            if rtype == self._AUTHORITY_TYPE_AUTHORITY and category_id not in authority_categories:
                session.add(AuthorityCategory(
                    authorityCategoryId=category_id,
                    name=category.title(),
                    description=None
                ))
                authority_categories.add(category_id)
            elif rtype == self._AUTHORITY_TYPE_INQUEST and category_id not in inquest_categories:
                session.add(InquestCategory(
                    inquestCategoryId=category_id,
                    name=category.title(),
                    description=None
                ))
                inquest_categories.add(category_id)
            session.commit()

            # Get keyword ID from keyword name (e.g., Cause-Fall from height -> CAUSE_FALL_FROM_HEIGHT).
            keyword_id = self._format_as_id(rkeyword)
            # Name keyword without category (e.g., Cause-Fall from height -> Fall from height)
            keyword_name = (rkeyword.split('-', 1)[1]) if '-' in rkeyword else rkeyword

            if rtype == self._AUTHORITY_TYPE_AUTHORITY:
                model = AuthorityKeyword(
                    authorityKeywordId=keyword_id,
                    authorityCategoryId=category_id,
                    name=keyword_name,
                    description=None,
                )
            elif rtype == self._AUTHORITY_TYPE_INQUEST:
                model = InquestKeyword(
                    inquestKeywordId=keyword_id,
                    inquestCategoryId=category_id,
                    name=keyword_name,
                    description=None,
                )

            session.add(model)
            session.flush()

            self._mapping_keyword_id[rkeyword] = keyword_id

        session.commit()

    def populate_authorities_and_inquests(self):
        print('[INFO] Populating authorities and inquests.')

        session = self._get_db_session()

        inquest_types = {
            'construction',
            'custody-inmate',
            'custody-police',
            'discretionary',
            'mining',
        }
        death_manners = {
            'accident',
            'homicide',
            'suicide',
            'natural',
            'undetermined',
        }

        for row in self._read_worksheet('Authorities'):
            (rserial, rname, _, rtype, rsynopsis, rkeywords, _, rquotes, rnotes, rprimary, rsourcerank, _,
                roverview, _, _, rjurisdiction, rsource, _, rprimarydoc, _, rcited, rrelated, _, _, _, rlastname,
                rgivennames, rage, rdeathdate, rcause, rinqtype, rpresidingofficer, rsex, rstart, rend) = row

            if not self._is_valid_authority_type(rtype):
                print('[WARNING] Unknown authority type: {}'.format(rtype))
                continue

            self._authority_data[rserial] = (rtype, rsource)

            if rtype == self._AUTHORITY_TYPE_AUTHORITY:
                authority = Authority(
                    primary=rprimary,
                    name=rname,
                    overview=roverview,
                    synopsis=rsynopsis,
                    quotes=rquotes,
                    notes=rnotes
                )
                session.add(authority)
                session.flush()
                authority_id = authority.authorityId
                self._authority_related[authority_id] = (rcited, rrelated)
                self._rel_authority_to_primary_document[rserial] = rprimarydoc
            elif rtype == self._AUTHORITY_TYPE_INQUEST:
                # Currently there are no inquests from outside of Canada.
                jurisdiction = 'CAD_' + rjurisdiction

                # Some inquests have their name prefixed with 'Inquest-'; this is redundant.
                if rname.startswith('Inquest-'):
                    rname = rname.replace('Inquest-', '', 1)

                # Parse manner of death (e.g., accident, homicide) and description from inquest synopsis.
                match = re.search(r'(?<=Manner of Death: )(.*)\s*((.|\n)*)', rsynopsis)
                if match is None:
                    # Assume that inquest synopsis only contains description of inquest.
                    synopsis = rsynopsis.strip()
                    death_manner_id = None
                else:
                    synopsis = match.group(2).strip()
                    inquest_death_manner = match.group(1).strip()
                    for death_manner in death_manners:
                        if inquest_death_manner.lower().startswith(death_manner[0]):
                            death_manner_id = self._format_as_id(death_manner)
                            break
                    else:
                        print('[WARNING] Invalid manner of death: {}'.format(inquest_death_manner))

                inquest = Inquest(
                    jurisdictionId=jurisdiction,
                    primary=rprimary,
                    name=rname,
                    overview=None,
                    synopsis=synopsis,
                    notes=rnotes,
                    presidingOfficer=rpresidingofficer,
                    start=self._format_date(rstart),
                    end=self._format_date(rend),
                    sittingDays=None,
                    exhibits=None,
                )
                session.add(inquest)
                session.flush()
                authority_id = inquest.inquestId

                # Get inquest type.
                if rinqtype.startswith('Mandatory-'):
                    # An inquest is either 'Discretionary' or 'Mandatory-<reason>'; this makes 'Mandatory' redundant.
                    inquest_type = rinqtype.replace('Mandatory-', '')
                else:
                    inquest_type = rinqtype
                if inquest_type.lower() not in inquest_types:
                    print('[WARNING] Invalid inquest type: {}'.format(inquest_type))
                    inquest_type_id = None
                else:
                    inquest_type_id = self._format_as_id(inquest_type)

                deceased = Deceased(
                    inquestId=authority_id,
                    inquestTypeId=inquest_type_id,
                    deathMannerId=death_manner_id,
                    deathCause=rcause,
                    deathDate=self._format_date(rdeathdate),
                    lastName=rlastname.title(),
                    givenNames=rgivennames.title(),
                    age=rage,
                    sex=None
                )
                session.add(deceased)
                session.flush()

            self._mapping_authority_id[rserial] = authority_id

        session.commit()

    def populate_authority_relationships(self):
        print('[INFO] Populating authority relationships.')

        session = self._get_db_session()

        for (authority_id, (cited, related)) in self._authority_related.items():
            # Map authority to its cited authorities and related authorities.
            if cited is not None:
                for authority in cited.split('\n'):
                    if authority == '':
                        continue

                    # Ignore references to authorities which do not exist.
                    if authority not in self._authority_data:
                        print(
                             '[WARNING] Invalid authority {} cited by authority with ID: {}'
                            .format(authority, authority_id)
                        )
                        continue

                    authority_type, authority_source = self._authority_data[authority]

                    # Ignore references to inquests.
                    if authority_type == self._AUTHORITY_TYPE_INQUEST:
                        print(
                             '[WARNING] Inquest {} cited by authority with ID: {}'
                            .format(authority, authority_id)
                        )
                        continue

                    session.add(AuthorityCitations(
                        authorityId=authority_id,
                        citedAuthorityId=self._mapping_authority_id[authority],
                    ))
                    session.flush()

            if related is not None:
                for authority in related.split('\n'):
                    if authority == '':
                        continue

                    # Ignore references to authorities which do not exist.
                    if authority not in self._authority_data:
                        print(
                             '[WARNING] Invalid authority {} related to authority with ID: {}'
                            .format(authority, authority_id)
                        )
                        continue

                    authority_type, authority_source = self._authority_data[authority]

                    if authority_type == self._AUTHORITY_TYPE_INQUEST:
                        session.add(AuthorityInquests(
                            authorityId=authority_id,
                            inquestId=self._mapping_authority_id[authority],
                        ))
                    else:
                        session.add(AuthorityRelated(
                            authorityId=authority_id,
                            relatedAuthorityId=self._mapping_authority_id[authority],
                        ))
                    session.flush()

        session.commit()

    def populate_authority_and_inquest_keywords(self):
        print('[INFO] Populating authority and inquest keywords.')

        session = self._get_db_session()

        for row in self._read_worksheet('Authorities'):
            rserial = row[0]
            rtype = row[3]
            rkeywords = row[5]

            if not self._is_valid_authority_type(rtype):
                print('[WARNING] Unknown authority type: {}'.format(rtype))
                continue

            for keyword in rkeywords.split(','):
                if keyword == '' or keyword == 'zz_NotYetClassified':
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
                        authorityId=self._mapping_authority_id[rserial],
                        authorityKeywordId=self._mapping_keyword_id[keyword],
                    )
                elif rtype == self._AUTHORITY_TYPE_INQUEST:
                    model = InquestKeywords(
                        inquestId=self._mapping_authority_id[rserial],
                        inquestKeywordId=self._mapping_keyword_id[keyword],
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

    def populate_documents(self):
        print('[INFO] Populating authority and inquest documents.')

        session = self._get_db_session()

        document_sources = set()

        for row in self._read_worksheet('Docs'):
            rauthorities, rserial, rshortname, rcitation, rdate, rlink, rlinktype = row

            # Create document source type (i.e., the location where the document is stored) if it does not exist.
            if 'inquests.ca' in rlinktype.lower():
                document_source = 'Inquests.ca'
            else:
                document_source = rlinktype
            document_source_id = self._format_as_id(document_source)
            if document_source_id not in document_sources:
                session.add(DocumentSource(
                    documentSourceId=document_source_id,
                    name=document_source,
                ))
                session.flush()
                document_sources.add(document_source_id)

            # Map authority or inquest to its documents.
            for authority in rauthorities.split('\n'):
                if authority == '':
                    continue

                # Ignore references to authorities which do not exist.
                if authority not in self._authority_data:
                    print(
                         '[WARNING] Invalid authority {} referenced by document with ID: {}'
                        .format(authority, rserial)
                    )
                    continue

                authority_type, authority_source = self._authority_data[authority]

                if authority_type == self._AUTHORITY_TYPE_AUTHORITY:
                    authority_document = AuthorityDocument(
                        authorityId=self._mapping_authority_id[authority],
                        authorityDocumentTypeId=None,
                        sourceId=self._mapping_source_id[authority_source],
                        primary=rcitation == self._rel_authority_to_primary_document[authority],
                        name=rshortname,
                        citation=rcitation,
                        created=self._format_date(rdate),
                    )
                    session.add(authority_document)
                    session.flush()
                    session.add(AuthorityDocumentLinks(
                        authorityDocumentId=authority_document.authorityDocumentId,
                        documentSourceId=document_source_id,
                        link=rlink,
                    ))
                    session.flush()
                elif authority_type == self._AUTHORITY_TYPE_INQUEST:
                    if rshortname.startswith('Inquest-'):
                        # Some inquest documents begin with 'Inquest-'; this is redundant.
                        document_name = rshortname.replace('Inquest-', '')
                    else:
                        document_name = rshortname
                    session.add(InquestDocument(
                        inquestId=self._mapping_authority_id[authority],
                        inquestDocumentTypeId=None,
                        documentSourceId=document_source_id,
                        name=document_name,
                        created=self._format_date(rdate),
                        link=rlink,
                    ))
                    session.flush()

        session.commit()


if __name__ == '__main__':
    data_path = sys.argv[1]
    db_url = sys.argv[2]
    Migrator(data_path, db_url)
