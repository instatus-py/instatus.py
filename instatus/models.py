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

class StatusPager:
    def __init__(self, *args):
        ...

    async def update(self, *args):
        ...

    async def delete(self, *args):
        ...


class Component:
    def __init__(self, *args):
        ...

    async def update(self, *args):
        ...

    async def delete(self, *args):
        ...


class Incident:
    def __init__(self, *args):
        ...

    async def update(self, *args):
        ...

    async def edit_update(self, *args):
        ...

    async def delete(self, *args):
        ...


class IncidentUpdate:
    def __init__(self, *args):
        ...

    async def update(self, *args):
        ...

    async def delete(self, *args):
        ...


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
