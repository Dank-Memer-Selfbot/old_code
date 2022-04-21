"""Contains functions for checking if a port is open using syn packets and a generator wrapper around it.

To be frank, I wasn't sure how to tackle this, so I started by doing some research on how masscan worked, and how I could send syn packets through python. I considered using python-masscan but that simply didn't have what I wanted, I want something nice, asynchronous, and customizable, which is only possible when you do something in house.

Resources -
- https://inc0x0.com/tcp-ip-packets-introduction/tcp-ip-packets-4-creating-a-syn-port-scanner/
For actual syn code in py, most of the function is based off of it.

- https://www.thepythoncode.com/article/syn-flooding-attack-using-scapy-in-python
To understand how a normal TCP connection works and how this is different.
"""

import socket


class Syn:
    def __init__(self):
        ...

    def _ping(self, host: str, port: int, timeout: int = 3):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        try:
            s.connect((host, port))
            s.close()
            return True
        except ConnectionRefusedError:
            return True
        except TimeoutError:
            return False
        except Exception as exc:
            return False

    async def ping(self, host: str, port: int):
        ...
