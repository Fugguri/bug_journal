from datetime import datetime, date


def parse_date_from_string(date_string: str) -> datetime:
    _date = datetime.strptime(date_string, '%d.%m.%Y')
    return _date


def get_now_datetime() -> str:
    return datetime.now().strftime('%d.%m.%Y %H:%M:%S')


def get_now_date() -> str:
    return datetime.now().strftime('%d.%m.%Y')
