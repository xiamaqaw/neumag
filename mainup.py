import requests
import asyncio

async def up():
    while True:
        r = requests.get("http://openaidiscordbot.tembultov.repl.co/", verify=False)
        await asyncio.sleep(300)

asyncio.run(up())