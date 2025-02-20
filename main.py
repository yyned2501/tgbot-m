import sys

if sys.platform != "win32":
    import uvloop

    uvloop.install()

import asyncio
from app import start_app

if __name__ == "__main__":
    asyncio.run(start_app())
