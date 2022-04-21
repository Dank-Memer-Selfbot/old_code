import ipaddress
from rich.console import Console
from . import ping, syn

ping = ping.Ping
syn = syn.Syn
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


async def human():
    ports = console.input("List of ports?\nExample: 25565, 25566\n> ").split(", ")
    ip_range = console.input("IP Range?\nExample: 0.0.0.0/0\n> ")
    s = scan(ipaddress.ip_network(ip_range), ports=ports)
    for data in s:
        status = data[0]
        info = data[1]
        if not status:
            console.log(info + " bad")
            continue
        if status:
            console.log(info)
            console.log("based")
            continue


if __name__ == "__main__":
    import asyncio

    asyncio.run(human())
