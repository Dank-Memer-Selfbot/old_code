import ipaddress
from rich.console import Console
from typing import Dict, List, AsyncGenerator

# --- Constants --- #

console = Console()

# --- Ping --- #

from mcstatus import JavaServer
from typing import Dict


class Ping:
    def __init__(self):
        ...

    async def ping(
        self, ip_address, port: int
    ) -> dict[str, str | int | Dict[str, str | int | list]] | Exception:
        """Fully and asynchronously pings a minecraft server.

        Args:
            ip_address (str): The server's IP Address.
            port (int): The port to ping on.

        Returns:
            dict[str, str | int | Dict[str, str | int | list]] | Exception: The server's response data.

            {
                "version": {
                    "name": "1.8.7",
                    "protocol": 47
                },
                "players": {
                    "max": 100,
                    "online": 5,
                    "sample": [
                        {
                            "name": "thinkofdeath",
                            "id": "4566e69f-c907-48ee-8d71-d7ba5aa00d20"
                        }
                    ]
                },
                "description": {
                    "text": "Hello world"
                },
                "favicon": "data:image/png;base64,<data>"
            }

            version: Dict[str, str | int]
            players: Dict[str, str | int | List[Dict[str, str]]]
            description: Dict[str, str]
            favicon: str
        """
        try:
            data = await JavaServer(host=ip_address, port=port).async_status()
            data = data.raw
        except Exception as exc:
            data = exc
        return data

# --- Syn --- #

"""Contains functions for checking if a port is open using syn packets and a generator wrapper around it.

To be frank, I wasn't sure how to tackle this, so I started by doing some research on how masscan worked, and how I could send syn packets through python. I considered using python-masscan but that simply didn't have what I wanted, I want something nice, asynchronous, and customizable, which is only possible when you do something in house.

Resources -
- https://inc0x0.com/tcp-ip-packets-introduction/tcp-ip-packets-4-creating-a-syn-port-scanner/
For actual syn code in py, most of the function is based off of it.

- https://www.thepythoncode.com/article/syn-flooding-attack-using-scapy-in-python
To understand how a normal TCP connection works and how this is different.
"""

import socket
from awaits.awaitable import awaitable


class Syn:
    def __init__(self):
        ...

    @awaitable
    def ping(self, host: str, port: int, timeout: int = 3) -> bool:
        """Pings an IP Address using sync packets, sourced from https://github.com/pdrb/synping/blob/master/synping/synping.py

        Args:
            host (str): The IP Address to ping.
            port (int): The port to ping on.
            timeout (int, optional): How long the socket should wait before timing out. Defaults to 3 seconds.

        Returns:
            bool: Whether or not the port is open, as well as if the host is alive.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        try:
            s.connect((host, port))
            s.close()
            return True
        except ConnectionRefusedError:
            return False
        except TimeoutError:
            return False
        except Exception as exc:
            return False

# --- Scanning --- #

syn = Syn()
ping = Ping()

async def scan(ip_range: ipaddress.IPv4Network, ports: List[int]) -> AsyncGenerator:
    """Meant for scanning an IP Block for minecraft servers."""

    for ip_address in ip_range:
        for port in ports:
            ip = f"{str(ip_address)}:{port}"
            if not await syn.ping(ip, port):
                yield False, ip, 'syn', None
                continue
            data = await ping.ping(ip, port)
            if isinstance(data, Exception):
                yield False, ip, 'err', data
                continue
            yield True, data.raw, 'suc', None


async def human():
    ports = console.input("List of ports?\nExample: 25565, 25566\n> ").split(", ")
    ip_range = console.input("IP Range?\nExample: 0.0.0.0/0\n> ")
    s = scan(ipaddress.ip_network(ip_range), ports=ports)
    async for data in s:
        status = data[0]
        info = data[1]
        if not status:
            console.log(data)
            console.log("bad")
            continue
        if status:
            console.log(data)
            console.log("based")
            continue


if __name__ == "__main__":
    import asyncio

    asyncio.run(human())
