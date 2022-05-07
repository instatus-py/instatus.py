import json
import datetime


def to_json(obj):
    return json.dumps(obj, separators=(',', ':'), ensure_ascii=True)

def _parse_ratelimit_header(request, *, use_clock=False):
    reset_after = request.headers.get('X-Ratelimit-Reset-After')
    if use_clock or not reset_after:
        utc = datetime.timezone.utc
        now = datetime.datetime.now(utc)
        reset = datetime.datetime.fromtimestamp(float(request.headers['X-Ratelimit-Reset']), utc)
        return (reset - now).total_seconds()
    else:
        return float(reset_after)