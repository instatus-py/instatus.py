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

import requests

baseurl = "https://api.instatus.com/v1/"


class StatusPager:
    def __init__(self, *args):
        ...

    async def get(self, api_key):
        """
        Get a Status page from the instastatus api
        """
        headers = {"Content-Type": "application/json"}
        req = requests.get(f'{baseurl}pages',
                           headers=headers,
                           auth=api_key
                           )
        return req.json()

    async def create(self, api_key):
        """
        Create a Status page from the instastatus api
        """
        headers = {"Content-Type": "application/json"}
        req = requests.post(f'{baseurl}pages',
                            headers=headers,
                            auth=api_key
                            )
        return req.json()

    async def update(self, api_key, page_id):
        """
        Update a Status page from the instastatus api
        """
        headers = {"Content-Type": "application/json"}
        req = requests.put(f'{baseurl}:{page_id}',
                           headers=headers,
                           auth=api_key
                           )
        return req.json()

    async def delete(self, api_key, page_id):
        """
        Delete a Status page from the instastatus api
        """
        headers = {"Content-Type": "application/json"}
        req = requests.delete(f'{baseurl}:{page_id}',
                              headers=headers,
                              auth=api_key
                              )
        return req.json()


class Component:
    def __init__(self, *args):
        ...

    async def delete(self, api_key, page_id, component_id):
        """
        Delete a component from the instastatus api
        """
        headers = {"Content-Type": "application/json"}
        req = requests.delete(f'{baseurl}:{page_id}/components/:{component_id}',
                              headers=headers,
                              auth=api_key
                              )
        return req.json()

    async def create(self, api_key, page_id):
        """
        Create a component from the instastatus api
        """
        headers = {"Content-Type": "application/json"}
        req = requests.post(f'{baseurl}:{page_id}/components',
                            headers=headers,
                            auth=api_key
                            )
        return req.json()

    async def update(self, api_key, page_id, component_id):
        """
        Update a component from the instastatus api
        """
        headers = {"Content-Type": "application/json"}
        req = requests.put(f'{baseurl}:{page_id}/components/:{component_id}',
                           headers=headers,
                           auth=api_key
                           )
        return req.json()

    async def getall(self, api_key, page_id):
        """
        Get all components from the instastatus api
        """
        headers = {"Content-Type": "application/json"}
        req = requests.get(f'{baseurl}:{page_id}/components',
                           headers=headers,
                           auth=api_key
                           )
        return req.json()

    async def get(self, api_key, page_id, component_id):
        """
        Get a specific component from the instastatus api
        """
        headers = {"Content-Type": "application/json"}
        req = requests.get(f'{baseurl}:{page_id}/components/:{component_id}',
                           headers=headers,
                           auth=api_key
                           )
        return req.json()


class Incident:
    def __init__(self, *args):
        ...

    async def getall(self, api_key, page_id):
        """
        Get all incidents from the instastatus api
        """
        headers = {"Content-Type": "application/json"}
        req = requests.get(f'{baseurl}:{page_id}/incident',
                           headers=headers,
                           auth=api_key
                           )
        return req.json()

    async def get(self, api_key, page_id, incident_id):
        """
        Get a incident from the instastatus api
        """
        headers = {"Content-Type": "application/json"}
        req = requests.get(f'{baseurl}:{page_id}/incidents/:{incident_id}',
                           headers=headers,
                           auth=api_key
                           )
        return req.json()

    async def create(self, api_key, page_id):
        """
        Create a incident from the instastatus api
        """
        headers = {"Content-Type": "application/json"}
        req = requests.post(f'{baseurl}:{page_id}/incidents',
                            headers=headers,
                            auth=api_key
                            )
        return req.json()

    async def update(self, api_key, page_id, incident_id):
        """
        Update a incident from the instastatus api
        """
        headers = {"Content-Type": "application/json"}
        req = requests.put(f'{baseurl}:{page_id}/incidents/:{incident_id}',
                           headers=headers,
                           auth=api_key
                           )
        return req.json()

    async def delete(self, api_key, page_id, incident_id):
        """
        Delete a incident from the instastatus api
        """
        headers = {"Content-Type": "application/json"}
        req = requests.post(f'{baseurl}:{page_id}/incidents/:{incident_id}',
                            headers=headers,
                            auth=api_key
                            )
        return req.json()


class IncidentUpdate:
    def __init__(self, *args):
        ...

    async def get(self, api_key, page_id, incident_id, incident_update_id):
        """
        Get a incident from the instastatus api
        """
        headers = {"Content-Type": "application/json"}
        req = requests.get(f'{baseurl}:{page_id}/incidents/:{incident_id}/incident-updates/:{incident_update_id}',
                           headers=headers,
                           auth=api_key
                           )
        return req.json()

    async def add(self, api_key, page_id, incident_id):
        """
        Get a incident from the instastatus api
        """
        headers = {"Content-Type": "application/json"}
        req = requests.post(f'{baseurl}:{page_id}/incidents/:{incident_id}/incident-updates',
                            headers=headers,
                            auth=api_key
                            )
        return req.json()

    async def edit(self, api_key, page_id, incident_id, incident_update_id):
        """
        Get a incident from the instastatus api
        """
        headers = {"Content-Type": "application/json"}
        req = requests.put(f'{baseurl}:{page_id}/incidents/:{incident_id}/incident-updates/:{incident_update_id}',
                           headers=headers,
                           auth=api_key
                           )
        return req.json()

    async def delete(self, api_key, page_id, incident_id, incident_update_id):
        """
        Get a incident from the instastatus api
        """
        headers = {"Content-Type": "application/json"}
        req = requests.delete(f'{baseurl}:{page_id}/incidents/:{incident_id}/incident-updates/:{incident_update_id}',
                              headers=headers,
                              auth=api_key
                              )
        return req.json()


class Maintenance:
    def __init__(self, *args):
        ...

    async def update(self, *args):
        ...

    async def edit_update(self, *args):
        ...

    async def delete(self, *args):
        ...


class MaintenanceUpdate:
    def __init__(self, *args):
        ...

    async def update(self, *args):
        ...

    async def delete(self, *args):
        ...


class TeamMember:
    def __init__(self, *args):
        ...

    async def delete(self, *args):
        ...


class Subscriber:
    def __init__(self, *args):
        ...

    async def delete(self, *args):
        ...


class Metric:
    def __init__(self, *args):
        ...

    async def update(self, *args):
        ...

    async def delete(self, *args):
        ...

    async def add_datapoint(self, *args):
        ...

    async def add_datapoints(self, *args):
        ...

    async def delete_datapoint(self, *args):
        ...


class UserProfile:
    def __init__(self, *args):
        ...
