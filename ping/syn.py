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
