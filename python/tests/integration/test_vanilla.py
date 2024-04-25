import asyncio

import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def my_fixture():

    await asyncio.sleep(1)

    yield 1

    await asyncio.sleep(1)


@pytest.mark.asyncio
async def test_me(my_fixture):

    a = my_fixture
    print(a)
