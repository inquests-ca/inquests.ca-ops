"""
Migrates data from Excel to local database and optionally production.

NOTE: this script should only be run locally since the MySQL password is passed
in the CLI.
"""

import argparse
import re
import subprocess

from logger import logger
from migration import Migrator

LOCAL_DATABASE_URL = "mysql+pymysql://root@127.0.0.1:3306/"


def _init_db():
    logger.info('Initializing DB schema.')

    with open("../mysql_workbench/inquestsca.sql", "r") as mysql_script:
        subprocess.run(['mysql', '-u', 'root'], stdin=mysql_script, check=True)


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', help='Directory containing data to be processed')
    parser.add_argument('--documents', help='Directory containing documents')
    parser.add_argument('--db', help='Local database')
    parser.add_argument('--upload', action='store_true', help='Whether to upload documents to AWS S3')
    return parser.parse_args()


def _migrate_prod(local_database):
    match = None
    while match is None:
        database_url_input = input('Please enter production database URL: ')
        match = re.match(
            r'mysql://(.*?):(.*?)@(.*?):(\d+?)/(.*)',
            database_url_input
        )
        if match is None:
            print("Invalid database URL, please try again.")
    user, password, host, port, database = match.groups()

    mysqldump_process = subprocess.Popen(
        ['mysqldump', local_database, '-u', 'root'],
        stdout=subprocess.PIPE,
    )

    # TODO: avoid passing MySQL password through CLI.
    mysql_args = [
        'mysql',
        '--user={}'.format(user),
        '--password={}'.format(password),
        '--host={}'.format(host),
        '--port={}'.format(port),
        '--database={}'.format(database),
    ]
    subprocess.run(mysql_args, stdin=mysqldump_process.stdout, check=True)

    logger.info('Successfully promoted data to production.')


if __name__ == '__main__':
    _init_db()

    args = _parse_args()
    migrator = Migrator(
        args.data,
        args.documents,
        LOCAL_DATABASE_URL + args.db,
        args.upload
    )

    migrator.run()

    migrate_prod = input('Promote data to production? [Y/n]: ')
    if migrate_prod == 'Y':
        _migrate_prod(args.db)

    logger.info('Script completed without errors.')
