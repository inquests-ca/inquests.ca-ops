import datetime
import re


def format_as_id(name):
    """Formats string to an appropriate ID."""
    return (
        name
            .upper()
            .replace('-', '_')
            .replace(' ', '_')
            .replace('.', '_')
            .replace('/', '_')
    )


def nullable_to_string(string):
    """Done to satisfy NULL constraints."""
    if string is None:
        return ''
    return format_string(string)


def string_to_nullable(string):
    """If string is empty, return None"""
    if string is None or string.strip() == '':
        return None
    return format_string(string)


def format_string(string):
    """Format string before inserting into database. Currently only trims whitespace."""
    if string is None:
        return None
    return string.strip()


def format_date(date):
    """Format date string into SQL-compatible date."""
    if isinstance(date, datetime.datetime):
        return date
    elif date is None or date == '':
        return None
    elif re.match(r'\d{4}-\d{2}-\d{2}', date) is not None:
        # Date is already in valid format.
        return date
    else:
        match = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', date)
        if match is not None and len(match.groups()) == 3:
            (month, day, year) = match.groups()
            return "{}-{}-{}".format(year, month, day)
        else:
            raise ValueError('Invalid date: {}'.format(date))


def get_year_from_date(date):
    """Get year from date; note that date may be one of many types or formats."""
    if isinstance(date, datetime.datetime):
        return str(date.year)
    elif date is None or date == '':
        return None
    elif re.match(r'\d{4}-\d{2}-\d{2}', date) is not None:
        return date[:4]
    elif re.match(r'\d{1,2}/\d{1,2}/\d{4}', date) is not None:
        return date[-4:]
    else:
        raise ValueError('Invalid date: {}'.format(date))
