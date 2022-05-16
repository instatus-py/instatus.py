# -*- coding: utf-8 -*-
"""
The MIT License (MIT)

Copyright (c) 2022-present mccoderpy & McJojo22


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

import sys
import logging
import asyncio
import threading
from concurrent.futures import TimeoutError
from typing import Optional, Union, List, Tuple, Any, Dict, Awaitable, TypeVar, TYPE_CHECKING

from .http_requests import HTTPClient

if TYPE_CHECKING:
    import aiohttp

log = logging.getLogger(__name__)

__all__ = ('StatusClient',)

T = TypeVar("T")


def _start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


_LOOP = asyncio.new_event_loop()
_LOOP_THREAD = threading.Thread(
    target=_start_background_loop, args=(_LOOP,), daemon=True
)
_LOOP_THREAD.start()


def asyncio_run(coro: Awaitable[T], timeout=30, ignore_no_result=True) -> T:
    """
    Runs the coroutine in an event loop running on a background thread,
    and blocks the current thread until it returns a result.
    This plays well with gevent, since it can yield on the Future result call.

    Parameters
    ----------

    :param coro: A coroutine, typically an async method
    :param timeout: How many seconds we should wait for a result before raising an error
    :param ignore_no_result: Whether to ignore if the result timeouts
    """
    future = asyncio.run_coroutine_threadsafe(coro, _LOOP)
    try:
        result = future.result(timeout=timeout)
    except TimeoutError:
        if ignore_no_result:
            return None
        raise
    return result


def asyncio_gather(*futures, return_exceptions=False):
    """
    A version of asyncio.gather that runs on the internal event loop
    """
    return asyncio.gather(*futures, loop=_LOOP, return_exceptions=return_exceptions)


def _cancel_tasks(loop):
    try:
        task_retriever = asyncio.Task.all_tasks
    except AttributeError:
        # future proofing for 3.9 I guess
        task_retriever = asyncio.all_tasks

    tasks = {t for t in task_retriever(loop=loop) if not t.done()}

    if not tasks:
        return

    log.info('Cleaning up after %d tasks.', len(tasks))
    for task in tasks:
        task.cancel()

    loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
    log.info('All tasks finished cancelling.')

    for task in tasks:
        if task.cancelled():
            continue
        if task.exception() is not None:
            loop.call_exception_handler({
                'message': 'Unhandled exception during StatusClient.run shutdown.',
                'exception': task.exception(),
                'task': task
            })


async def _cleanup_loop(loop):
    try:
        _cancel_tasks(loop)
        if sys.version_info >= (3, 6):
            loop.run_until_complete(loop.shutdown_asyncgens())
    finally:
        log.info('Closing the event loop.')
        await loop.close()


class StatusClient:
    def __init__(self,
                 api_key: str,
                 *,
                 loop: Optional[asyncio.AbstractEventLoop] = _LOOP,
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
        self.loop = self._http.loop

    def __del__(self):
        if not self.loop.is_closed():
            if not self._http.is_closed:
                asyncio_run(self.close())

    async def close(self):
        if not self.loop.is_closed():
            if not self._http.is_closed:
                await self._http.close()

    def run(self, coro: T, timeout=None):
        asyncio_run(coro, timeout=timeout)
        _LOOP.create_task(self.close())

    async def fetch_summary(self, prod_name: str):
        return await self._http.get_summary(prod_name)

    async def get_status_pages(self):
        data = await self._http.get_status_pages()
        return data

    async def create_status_page(self, data):
        return await self._http.create_status_page(data)

    async def update_status_page(self, page_id: str, data):
        return await self._http.update_status_page(page_id, data)

    async def delete_status_page(self, page_id: str):
        return await self._http.delete_status_page(page_id)

    async def get_component(self, page_id: str):
        return await self._http.delete_status_page(page_id)

    async def update_component(self, page_id: str, component_id: str, data):
        return await self._http.update_component(page_id, component_id, data)

    async def delete_component(self, page_id: str, component_id: str):
        return await self._http.delete_component(page_id, component_id)

    async def get_incident(self, page_id: str, incident_id: str):
        return await self._http.get_incident(page_id, incident_id)

    async def getall_incidents(self, page_id: str):
        return await self._http.get_all_incidents(page_id)

    async def add_incident(self, page_id: str, data):
        return await self._http.add_incident(page_id, data)

    async def update_incident(self, page_id: str, incident_id: str, data):
        return await self._http.update_incident(page_id, incident_id, data)

    async def delete_incident(self, page_id: str, incident_id: str):
        return await self._http.delete_incident(page_id, incident_id)

    async def get_incident_update(self, page_id: str, incident_id: str, incident_update_id: str):
        return await self._http.get_incident_update(page_id, incident_id, incident_update_id)

    async def add_incident_update(self, page_id: str, incident_id: str, data):
        return await self._http.add_incident_update(page_id, incident_id, data)

    async def edit_incident_update(self, page_id: str, incident_id: str, incident_update_id: str, data):
        return await self._http.edit_incident_update(page_id, incident_id, incident_update_id, data)

    async def delete_incident_update(self, page_id: str, incident_id: str, incident_update_id: str):
        return await self._http.delete_incident_update(page_id, incident_id, incident_update_id)

    async def get_maintenance(self, page_id: str, incident_id: str):
        return await self._http.get_maintenance(page_id, incident_id)

    async def get_all_maintenances(self, page_id: str):
        return await self._http.get_all_maintenances(page_id)