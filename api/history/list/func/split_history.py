import datetime

from hooks.db.history_db import History


def convert2datetime(date_str):
    return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")


def remove_time(dt):
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def labeling(delta: datetime.timedelta, label):
    if delta == datetime.timedelta(days=0):
        return "today"
    elif delta == datetime.timedelta(days=1):
        return "yesterday"
    elif delta == datetime.timedelta(weeks=1):
        return "last week"
    elif delta == datetime.timedelta(days=30):
        return "last month"
    else:
        return label


def split_by_date(data_list: list[History]):
    data_list.sort(key=lambda d: convert2datetime(d.timestamp), reverse=True)

    intervals = []
    idx = 0

    if idx >= len(data_list):
        return intervals

    today = remove_time(
        datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).replace(
            tzinfo=None
        )
    )
    last_date = remove_time(convert2datetime(data_list[0].timestamp))
    days_since_last = (today - last_date).days

    for day in range(days_since_last, days_since_last + 3):
        if idx >= len(data_list):
            return intervals
        curr_day = today - datetime.timedelta(days=day)
        next_day = curr_day + datetime.timedelta(days=1)
        entries = [
            d
            for d in data_list[idx:]
            if curr_day <= convert2datetime(d.timestamp) < next_day
        ]
        intervals.append(
            {
                "label": labeling(datetime.timedelta(days=day), f"{day} days ago"),
                "data": entries,
            }
        )
        idx += len(entries)

    for week in range(1, 4):
        if idx >= len(data_list):
            return intervals
        week_end = today - datetime.timedelta(weeks=week)
        entries = [
            d for d in data_list[idx:] if convert2datetime(d.timestamp) >= week_end
        ]
        intervals.append(
            {
                "label": labeling(datetime.timedelta(weeks=week), f"{week} weeks ago"),
                "data": entries,
            }
        )
        idx += len(entries)

    for month in range(1, 4):
        if idx >= len(data_list):
            return intervals
        month_end = today - datetime.timedelta(days=month * 30)
        entries = [
            d for d in data_list[idx:] if convert2datetime(d.timestamp) >= month_end
        ]
        intervals.append(
            {
                "label": labeling(
                    datetime.timedelta(days=month * 30), f"{month*30} days ago"
                ),
                "data": entries,
            }
        )
        idx += len(entries)

    return intervals
