First we scan the IP range using syn.py to find open servers, possibly through a generator, and then use ping.py to create a full tcp connection with the server to pull more info.

The plan is to make everything asynchronous and use asyncio.gather.

Methods -

I can either make it use a generator expression, or run the syn scanning first and the pinging later, which isn't that cool imo.

With a generator expression, we run the syn on an IP & port, it returns true if the port is open, false if not. If the generator yields true, we run ping.py and store the result.

```py
async def syn(ip, port):
    return True, False

async def scan(ip_range, ports):
    for ip in ip_range:
        for port in ports:
            if await syn(ip, port):
                yield f"{ip}:{port}"
```

Something in that vein, so I also have access to the raw syn func and a nice wrapper around it.