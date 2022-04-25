from prisma import Prisma
from prisma.models import Server, Player, Version, Maximum
from typing import Any, List, Optional, Dict

from rich.console import Console

console = Console()


class _Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(
                Prisma(auto_register=True), *args, **kwargs
            )
        return cls._instances[cls]


class Database(metaclass=_Singleton):
    def __init__(self, client):
        self.client = client
        self.connected = False

    async def connect(self):
        if self.connected:
            return self.client
        await self.client.connect()
        self.connected = True
        return self.client

    async def disconnect(self):
        if not self.connected:
            return self.client
        await self.client.disconnect()
        self.connected = False
        return self.client

    async def add_server(
        self, ip_address: str, data: Dict[str, Any], authenticated: bool
    ) -> bool:
        """Adds a server to the database:

        Parameters:
            ip_address (str): The IP Address or hostname of the server.
            description (str): The description (motd) of the server.
            online_players (int): The number of players currently on the server.
            maximum_players (int): The maximum number of players that can be on the server at once.
            version (Version): A version object containing the server's version name and protocol.
            players (List[Player]): A list of player objects on the server, the length of this list is the same as online_players. Each player has a username and uuid.
            favicon (Optional[str]): The server's favicon, may be null.

        Returns:
            True/False (bool): Whether or not the operation was successful.
        """
        # https://wiki.vg/Server_List_Ping

        await self.connect()

        try:
            protocol = int(data["version"]["protocol"])
        except ValueError:
            protocol = 0

        players = [
            await Player.prisma().create(data=data)
            for data in [
                {
                    "uuid": player_data["id"],
                    "username": player_data["name"],
                    "authenticated": True,
                }
                for player_data in data["players"]["sample"]
            ]
        ]
        console.log(players)
        console.log(dir(players[0]))

        ip: str = ip_address
        description = f"{data['description']['text']!a}"
        favicon: str = data["favicon"]

        version = {"name": data["version"]["name"], "protocol": protocol}
        version = await Version.prisma().create(data=version)
        console.log(dir(version))
        version = version.id

        online = f"{data['players']['online']!a}"
        maximum = f"{data['players']['max']!a}"
        minmax = {"online": online, "max": maximum}
        minmax = await Maximum.prisma().create(data=minmax)
        console.log(dir(minmax))
        minmax = minmax.id

        server = {
            "ip_address": ip,
            "description": description,
            "favicon": favicon,
            "versionId": version,
            "maximumId": minmax,
            "players": players,
        }

        await Server.prisma().create(data=server)

        await self.disconnect()


import asyncio

d = Database()
data = {
    "version": {"name": "1.8.7", "protocol": 47},
    "players": {
        "max": 100,
        "online": 5,
        "sample": [
            {"name": "thinkofdeath", "id": "4566e69f-c907-48ee-8d71-d7ba5aa00d20"}
        ],
    },
    "description": {"text": "Hello world"},
    "favicon": "data:image/png;base64,<data>",
}
asyncio.run(d.add_server("123", data, True))
