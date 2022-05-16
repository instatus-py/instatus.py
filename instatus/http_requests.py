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
import json
import logging
import asyncio
import aiohttp
import weakref
from urllib.parse import quote as _uriquote

from .errors import HTTPException, NotFound, Forbidden, InstatusServerError

from . import utils, __version__


log = logging.getLogger(__name__)


async def json_or_text(response):
    encoding = 'utf-8'
    content_type = None
    try:
        content_type, encoding = response.headers['content-type'].split('; charset=')
    except KeyError:
        # Thanks Cloudflare
        pass

    text = await response.text(encoding=encoding)
    if content_type == 'application/json':
        return json.loads(text)

    return text


class Route:
    BASE = 'https://api.instatus.com/'

    def __init__(self, method, path: str = None, full_url: str = None, **parameters):
        self.path = path
        self.method = method
        if full_url:
            url = self.path = full_url
        else:
            url = (self.BASE + self.path)
        if parameters:
            self.url = url.format(**{k: _uriquote(v) if isinstance(v, str) else v for k, v in parameters.items()})
        else:
            self.url = url

    @property
    def bucket(self):
        # the bucket is just method + path w/ major parameters
        return '{0.path}'.format(self)


class MaybeUnlock:
    def __init__(self, lock):
        self.lock = lock
        self._unlock = True

    def __enter__(self):
        return self

    def defer(self):
        self._unlock = False

    def __exit__(self, _type, value, traceback):
        if self._unlock:
            self.lock.release()


class HTTPClient:
    """Represents an HTTP client sending HTTP requests to the Instatus API."""

    SUCCESS_LOG = '{method} {url} has received {text}'
    REQUEST_LOG = '{method} {url} with {json} has returned {status}'

    def __init__(self,
                 api_key: str,
                 connector=None,
                 *,
                 proxy=None,
                 proxy_auth=None,
                 loop=None,
                 unsync_clock=True,
                 cookie_file=None,
                 http_kwargs: dict = {}):
        if not loop:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
        self.loop = loop
        self.connector = connector
        self.__session = aiohttp.ClientSession(loop=loop, cookies=cookie_file or aiohttp.CookieJar(), **http_kwargs)
        self._locks = weakref.WeakValueDictionary()
        self._global_over = asyncio.Event()
        self._global_over.set()
        self.api_key = api_key
        self.cookie_file = cookie_file
        self.http_kwargs = http_kwargs
        self.proxy = proxy
        self.proxy_auth = proxy_auth
        self.use_clock = not unsync_clock

        user_agent = 'APIWrapper (https://github.com/mccoderpy/instatus.py {0}) Python/{1[0]}.{1[1]} aiohttp/{2}'
        self.user_agent = user_agent.format(__version__, sys.version_info, aiohttp.__version__)

    def recreate(self):
        if self.__session.closed:
            self.__session = aiohttp.ClientSession(**self.http_kwargs)

    async def request(self, route: Route, *, files=None, form=None, **kwargs):
        bucket = route.bucket
        method = route.method
        url = route.url

        lock = self._locks.get(bucket)
        if lock is None:
            lock = asyncio.Lock()
            if bucket is not None:
                self._locks[bucket] = lock

        # header creation
        headers = {
            'User-Agent': self.user_agent,
            'X-Ratelimit-Precision': 'millisecond',
        }

        if self.api_key is not None:
            headers['Authorization'] = 'Bearer ' + self.api_key
        # some checking if it's a JSON request
        if 'json' in kwargs:
            kwargs['data'] = utils.to_json(kwargs.pop('json'))

        if 'content_type' in kwargs:
            headers['Content-Type'] = kwargs.pop('content_type')
        else:
            headers['Content-Type'] = 'application/json'
        kwargs['headers'] = headers

        # Proxy support
        if self.proxy is not None:
            kwargs['proxy'] = self.proxy
        if self.proxy_auth is not None:
            kwargs['proxy_auth'] = self.proxy_auth

        if not self._global_over.is_set():
            # wait until the global lock is complete
            await self._global_over.wait()

        await lock.acquire()
        with MaybeUnlock(lock) as maybe_lock:
            for tries in range(5):
                if files:
                    for f in files:
                        f.reset(seek=tries)

                if form:
                    form_data = aiohttp.FormData(quote_fields=False)
                    for params in form:
                        form_data.add_field(**params)
                    kwargs['data'] = form_data

                try:
                    async with self.__session.request(method, url, **kwargs) as r:
                        log.debug('%s %s with %s has returned %s', method, url, kwargs.get('data'), r.status)

                        # even errors have text involved in them so this is safe to call
                        data = await json_or_text(r)

                        # check if we have rate limit header information
                        remaining = r.headers.get('X-Ratelimit-Remaining')
                        if remaining == '0' and r.status != 429:
                            # we've depleted our current bucket
                            delta = utils._parse_ratelimit_header(r, use_clock=self.use_clock)
                            log.debug('A rate limit bucket has been exhausted (bucket: %s, retry: %s).', bucket, delta)
                            maybe_lock.defer()
                            self.loop.call_later(delta, lock.release)

                        # the request was successful so just return the text/json
                        if 300 > r.status >= 200:
                            log.debug('%s %s has received %s', method, url, data)
                            return data

                        # we are being rate limited
                        if r.status == 429:
                            if not r.headers.get('Via'):
                                # Banned by Cloudflare more than likely.
                                raise HTTPException(r, data)

                            fmt = 'We are being rate limited. Retrying in %.2f seconds. Handled under the bucket "%s"'

                            # sleep a bit
                            retry_after = data['retry_after'] / 1000.0
                            log.warning(fmt, retry_after, bucket)

                            # check if it's a global rate limit
                            is_global = data.get('global', False)
                            if is_global:
                                log.warning('Global rate limit has been hit. Retrying in %.2f seconds.', retry_after)
                                self._global_over.clear()

                            await asyncio.sleep(retry_after)
                            log.debug('Done sleeping for the rate limit. Retrying...')

                            # release the global lock now that the
                            # global rate limit has passed
                            if is_global:
                                self._global_over.set()
                                log.debug('Global rate limit is now over.')

                            continue

                        # we've received a 500 or 502, unconditional retry
                        if r.status in {500, 502}:
                            await asyncio.sleep(1 + tries * 2)
                            continue

                        # the usual error cases
                        if r.status == 403:
                            raise Forbidden(r, data)
                        elif r.status == 404:
                            raise NotFound(r, data)
                        elif r.status == 503:
                            raise InstatusServerError(r, data)
                        else:
                            raise HTTPException(r, data)

                # This is handling exceptions from the request
                except OSError as e:
                    # Connection reset by peer
                    if tries < 4 and e.errno in (54, 10054):
                        continue
                    raise

            # We've run out of retries, raise.
            if r.status >= 500:
                raise InstatusServerError(r, data)

            raise HTTPException(r, data)

    async def get_from_cdn(self, url):
        async with self.__session.get(url) as resp:
            if resp.status == 200:
                return await resp.read()
            elif resp.status == 404:
                raise NotFound(resp, 'asset not found')
            elif resp.status == 403:
                raise Forbidden(resp, 'cannot retrieve asset')
            else:
                raise HTTPException(resp, 'failed to get asset')

    # state management

    @property
    def is_closed(self):
        return self.__session.closed

    async def close(self):
        if self.__session:
            await self.__session.close()

    def get_summary(self, prod_name):
        return self.request(Route('GET', full_url=f'https://{prod_name}.instatus.com/summary.json'))

    # Status pager requests

    def get_status_pages(self):
        """
        Get a Status page from the instatus api
        """
        return self.request(Route('GET', f"v1/pages"))

    def create_status_page(self, data):
        """
        Create a Status page from the instatus api
        """
        return self.request(Route('POST', f"v1/pages"), json=data)

    def update_status_page(self, page_id, data):
        """
        Update a Status page from the instatus api
        """
        return self.request(Route('PUT', f"v1/{page_id}"), json=data)

    def delete_status_page(self, page_id):
        """
        Delete a Status page from the instatus api
        """
        return self.request(Route('DELETE', f"v1/{page_id}"))

    # Components requests

    def get_component(self, page_id, component_id):
        """
        Get a component from the instatus api
        """
        return self.request(Route('GET', f"v1/{page_id}/components/{component_id}"))

    def get_all_components(self, page_id):
        """
        Get a component from the instatus api
        """
        return self.request(Route('GET', f"v1/{page_id}/components"))

    def create_component(self, page_id, data):
        """
        Create a component from the instatus api
        """
        return self.request(Route('POST', f"v1/{page_id}/components"), json=data)

    def update_component(self, page_id, component_id, data):
        """
        Update a component from the instatus api
        """
        return self.request(Route('PUT', f"v1/{page_id}/components/{component_id}"), json=data)

    def delete_component(self, page_id, component_id):
        """
        Delete a component from the instatus api
        """
        return self.request(Route('DELETE', f"v1/{page_id}/components/{component_id}"))

    # Incident requests

    def get_incident(self, page_id, incident_id):
        """
        Get an incident from the instatus api
        """
        return self.request(Route('GET', f"v1/{page_id}/incidents/{incident_id}"))

    def get_all_incidents(self, page_id):
        """
        Get all incidents from the instatus api
        """
        return self.request(Route('GET', f"v1/{page_id}/incidents"))

    def add_incident(self, page_id, data):
        """
        Add incident from the instatus api
        """
        return self.request(Route('POST', f"v1/{page_id}/incidents"), json=data)

    def update_incident(self, page_id, incident_id, data):
        """
        Update incident from the instatus api
        """
        return self.request(Route('PUT', f"v1/{page_id}/incidents/{incident_id}"), json=data)

    def delete_incident(self, page_id, incident_id):
        """
        Delete incident from the instatus api
        """
        return self.request(Route('DELETE', f"v1/{page_id}/incidents/{incident_id}"))

    # Incident update requests

    def get_incident_update(self, page_id, incident_id, incident_update_id):
        """
        Get an incident update from the instatus api
        """
        return self.request(Route('GET', f"v1/{page_id}/incidents/{incident_id}/incident-updates/{incident_update_id}"))

    def add_incident_update(self, page_id, incident_id, data):
        """
        Add an incident update from the instatus api
        """
        return self.request(Route('POST', f"v1/{page_id}/incidents/{incident_id}/incident-updates"), json=data)

    def edit_incident_update(self, page_id, incident_id, incident_update_id, data):
        """
        Update a incident update from the instatus api
        """
        return self.request(Route('PUT', f"v1/{page_id}/incidents/{incident_id}/incident-updates/{incident_update_id}"), json=data)

    def delete_incident_update(self, page_id, incident_id, incident_update_id):
        """
        Delete an incident update from the instatus api
        """
        return self.request(Route('DELETE', f"v1/{page_id}/incidents/{incident_id}/incident-updates/{incident_update_id}"))

    # Maintenances

    def get_maintenance(self, page_id, maintenance_id):
        """
        Get a maintenance from the instatus api
        """
        return self.request(Route('GET', f"v1/{page_id}/maintenances/{maintenance_id}"))

    def get_all_maintenances(self, page_id):
        """
        Get all maintenances from the instatus api
        """
        return self.request(Route('GET', f"v1/{page_id}/maintenances"))

    def add_maintenance(self, page_id, data):
        """
        Add a maintenance from the instatus api
        """
        return self.request(Route('POST', f"v1/{page_id}/maintenances"), json=data)

    def update_maintenance(self, page_id, maintenance_id, data):
        """
        Update a maintenance from the instatus api
        """
        return self.request(Route('PUT', f"v1/{page_id}/maintenances/{maintenance_id}"), json=data)

    def delete_maintenance(self, page_id, maintenance_id):
        """
        Delete a maintenance from the instatus api
        """
        return self.request(Route('DELETE', f"v1/{page_id}/maintenances/{maintenance_id}"))

    # Maintenances update

    def get_maintenance_update(self, page_id, maintenance_id, maintenance_update_id):
        """
        Get a maintenance update from the instatus api
        """
        return self.request(Route('GET', f"v1/{page_id}/maintenances/{maintenance_id}/maintenance-updates/{maintenance_update_id}"))

    def add_maintenance_update(self, page_id, maintenance_id, data):
        """
        Create a maintenance update from the instatus api
        """
        return self.request(Route('POST', f"v1/{page_id}/maintenances/{maintenance_id}/maintenance-updates"), json=data)

    def edit_maintenance_update(self, page_id, maintenance_id, maintenance_update_id, data):
        """
        Update a maintenance update from the instatus api
        """
        return self.request(Route('PUT', f"v1/{page_id}/maintenances/{maintenance_id}/maintenance-updates/{maintenance_update_id}"), json=data)

    def delete_maintenance_update(self, page_id, maintenance_id, maintenance_update_id):
        """
        Delete a maintenance update from the instatus api
        """
        return self.request(Route('DELETE', f"v1/{page_id}/maintenances/{maintenance_id}/maintenance-updates/{maintenance_update_id}"))

    # Teammate requests

    def get_teammates(self, page_id):
        """
        Get teammate from the instatus api
        """
        return self.request(Route('GET', f"v1/{page_id}/team"))

    def add_teammate(self, page_id, data):
        """
        Add a teammate from the instatus api
        """
        return self.request(Route('POST', f"v1/{page_id}/team"), json=data)

    def delete_teammate(self, page_id, member_id):
        """
        Delete a Teammate from the instatus api
        """
        return self.request(Route('DELETE', f"v1/{page_id}/team/{member_id}"))
