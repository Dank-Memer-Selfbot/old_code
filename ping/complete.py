import ipaddress
from rich.console import Console
from .ping import Ping
from .syn import Syn
from typing import Dict, List, AsyncGenerator

console = Console()
syn = Syn()
ping = Ping()


async def scan(ip_range: ipaddress.IPv4Network, ports: List[int]) -> AsyncGenerator:
    """Meant for scanning an IP Block for minecraft servers."""

    for ip_address in ip_range:
        for port in ports:
            ip = f"{str(ip_address)}:{port}"
            if not await syn.ping(ip):
                yield False, ip
                continue
            data = await ping.ping(ip)
            if isinstance(data, Exception):
                yield False, ip
                continue
            yield True, data.raw
