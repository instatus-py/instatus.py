# -*- coding: utf-8 -*-

"""
A async simple to use wrapper for the Instatus-API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Visit `Instatus <https://instatus.com/>`_
Visit `<Instatus-API: https://instatus.com/help/api/>`_


:copyright: (c) 2022-present mccoderpy
:license: MIT, see LICENSE for more details.
"""

__title__ = 'instatus'
__author__ = 'mccoderpy'
__license__ = 'MIT'
__copyright__ = 'Copyright 2022-present mccoderpy'
__version__ = '0.1a'


__path__ = __import__('pkgutil').extend_path(__path__, __name__)


import logging
from typing import NamedTuple
from typing_extensions import Literal

from . import utils
from .client import *
from .models import *
from .errors import *


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: Literal["alpha", "beta", "candidate", "final"]
    serial: int


version_info: VersionInfo = VersionInfo(major=0, minor=0, micro=1, releaselevel='alpha', serial=0)

logging.getLogger(__name__).addHandler(logging.NullHandler())

del logging, NamedTuple, Literal, VersionInfo



