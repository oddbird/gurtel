import datetime

import pytz

from gurtel import timezone


def test_now(monkeypatch):
    now = datetime.datetime(2013, 4, 24, 15, 47)

    class FakeDateTime(object):
        def utcnow(self):
            return now

    monkeypatch.setattr(timezone, 'datetime', FakeDateTime())

    assert timezone.now() == now.replace(tzinfo=pytz.utc)
