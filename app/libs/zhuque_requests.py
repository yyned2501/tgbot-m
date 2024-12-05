from copy import deepcopy
import aiohttp

from app.config import setting
from app import logger

timeout = aiohttp.ClientTimeout(total=5)
cookie_headers = {
    "x-csrf-token": setting["zhuque"]["x-csrf-token"],
    "cookie": setting["zhuque"]["cookie"],
}
listGenshinCharacter_url = "https://zhuque.in/api/gaming/listGenshinCharacter"


async def get(session: aiohttp.ClientSession, url, data=None, referer=None):
    headers = deepcopy(cookie_headers)
    headers["referer"] = referer
    async with session.get(url, headers=headers, data=data) as response:
        if response.status == 200:
            ret = await response.json()
            logger.debug(ret)
            return ret
        else:
            logger.error(f"Error: {response.status} {await response.text()}")
            return None


async def post(session: aiohttp.ClientSession, url, data=None, referer=None):
    headers = deepcopy(cookie_headers)
    headers["referer"] = referer
    async with session.post(url, headers=headers, data=data) as response:
        if response.status == 200:
            ret = await response.json()
            logger.debug(ret)
            return ret
        else:
            logger.error(f"Error: {response.status} {await response.text()}")
            return None


async def get_info():
    url = "https://zhuque.in/api/user/getMainInfo"
    referer = "https://zhuque.in/user/info"
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            info = await get(session, url, referer=referer)
            return info
        except:
            return None


if __name__ == "__main__":
    import asyncio

    asyncio.run(get_info())
