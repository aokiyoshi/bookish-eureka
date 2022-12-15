import asyncio
from client.gui_client import main

try:
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
except Exception as e:
    print(e)