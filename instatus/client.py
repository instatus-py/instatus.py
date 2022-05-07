# -*- coding: utf-8 -*-
"""
The MIT License (MIT)

Copyright (c) 2022-present mccoderpy


Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import asyncio
from os import PathLike
from pathlib import Path
from typing import Optional, Union, Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    import aiohttp

from .http_requests import HTTPClient

__all__ = ('StatusClient',)


class StatusClient:
    def __init__(self,
                 api_key: str,
                 *,
                 loop: Optional[asyncio.AbstractEventLoop] = None,
                 proxy: Optional[str] = None,
                 proxy_auth: Optional[str] = None,
                 connector: Optional[Any] = None,
                 cookie_file: Optional["aiohttp.CookieJar"] = None,
                 http_kwargs: Optional[Dict[str, Any]] = {}):
        self.api_key = api_key
        self._http = HTTPClient(
            api_key,
            connector,
            proxy=proxy,
            proxy_auth=proxy_auth,
            loop=loop,
            cookie_file=cookie_file,
            http_kwargs=http_kwargs
        )
        # self.loop = self._http.loop

    async def fetch_summary(self, prod_name: str):
        return await self._http.get_summary(prod_name)
