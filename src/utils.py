import datetime


def convert_date_us2kr(time):
    """
    Args:
        time: datatime.time

    """
    converted_time = datetime.datetime.strptime(time, '%Y-%m-%dT%H') + datetime.timedelta(hours=9)
    converted_date = converted_time.date()
    return converted_date


def check_date_in_period(date, period):
    today = datetime.date.today()
    diff_date = today - convert_date_us2kr(date)
    return diff_date.days <= int(period) - 1
