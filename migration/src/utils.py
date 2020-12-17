import datetime
import re


def format_as_id(name):
    """Formats string to an appropriate ID."""
    return (
        name
            .strip()
            .upper()
            .replace('-', '_')
            .replace(' ', '_')
            .replace('.', '_')
            .replace('/', '_')
    )


def format_as_keyword(name):
    """Formats string to an appropriate keyword."""
    if is_empty_string(name):
        return format_string(name)

    # Avoid use of string.capitalize() since it will lowercase all other letters, which is
    # undesired for abbreviations.
    return name.strip()[0].upper() + name.strip()[1:]


def nullable_to_string(string):
    """Done to satisfy NULL constraints."""
    if string is None:
        return ''
    return format_string(string)


def is_empty_string(string):
    """Return True if string is None or entirely whitespace."""
    return string is None or string.strip() == ''


def string_to_nullable(string):
    """If string is empty, return None"""
    if is_empty_string(string):
        return None
    return format_string(string)


def format_string(string):
    """Format string before inserting into database. Currently only trims whitespace."""
    # TODO: also perform spell and grammar checks?
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
