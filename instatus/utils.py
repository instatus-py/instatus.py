import json
import datetime
from itertools import chain
from typing import Union, Optional, List, Dict, Any


def to_json(obj):
    return json.dumps(obj, separators=(',', ':'), ensure_ascii=True)


def _parse_ratelimit_header(request, *, use_clock=False) -> float:
    reset_after = request.headers.get('X-Ratelimit-Reset-After')
    if use_clock or not reset_after:
        utc = datetime.timezone.utc
        now = datetime.datetime.now(utc)
        reset = datetime.datetime.fromtimestamp(float(request.headers['X-Ratelimit-Reset']), utc)
        return (reset - now).total_seconds()
    else:
        return float(reset_after)


def color_dict(obj: Union[Dict[str, Any], Any],
               *,
               highlight: str = None,
               key_color: str = '\033[91m',
               bool_color: str = '\33[94m',
               int_color: str = '\033[34m',
               str_color: str = '\033[93m',
               highlight_color_fg: str = '\033[97m',
               highlight_color_bg: str = '\033[43m',
               __is_key=False) -> Dict[str, Any]:
    if not isinstance(obj, (dict, list, tuple, set)):
        if isinstance(obj, (bool, type(None))):
            c_type = bool_color
            obj = f'{bool_color}{obj}\033[0m'
        elif isinstance(obj, (int, float)):
            c_type = int_color
            obj = f'{int_color}{obj}\033[0m'
        elif isinstance(obj, str):
            c_type = str_color
            if not __is_key:
                obj = f'{str_color}\'{obj}\'\033[0m'
            else:
                obj = f'{key_color}{obj}\033[0m'
        else:
            c_type = '\033[39m'
        if highlight:
            if not isinstance(highlight, (list, tuple, set)):
                highlight = [highlight]
            for to_highlight in highlight:
                obj = str(obj).replace(str(to_highlight), f'{highlight_color_fg}{highlight_color_bg}{to_highlight}\033[49m{c_type}')

        return obj
    else:
        o_type = obj.__class__
        colored_obj = o_type()
        if isinstance(obj, dict):
            for key, value in obj.items():
                colored_obj[color_dict(key, key_color=key_color, bool_color=bool_color, int_color=int_color, str_color=str_color, highlight=highlight, __is_key=True)] = color_dict(value, key_color=key_color, bool_color=bool_color, int_color=int_color, str_color=str_color, highlight=highlight)
        else:
            for value in obj:
                if isinstance(value, (dict, list, tuple)):
                    colored_obj.__iadd__([color_dict(value, key_color=key_color, bool_color=bool_color, int_color=int_color, str_color=str_color, highlight=highlight)])
                else:
                    colored_obj = o_type(chain(colored_obj, [color_dict(value, bool_color=bool_color, int_color=int_color, str_color=str_color, highlight=highlight)]))
        return colored_obj


def color_dumps(obj: Dict[str, Any], highlight: Optional[Union[str, List[str]]] = None, **kwargs):
    return json.dumps(color_dict(obj, highlight=highlight, **kwargs), separators=(', ', '\033[31m:\033[0m '), indent=4).replace('\\u001b', '\033').replace('"', '')


def color_print(obj: Dict[str, Any], highlight: Optional[Union[str, List[str]]] = None, print__kwargs={}, **kwargs):
    print(color_dumps(obj, highlight, **kwargs), **print__kwargs)
