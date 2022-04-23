from prisma import Prisma
from prisma.models import Server, Player, Version
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

    async def add_server(self, ip_address: str, data: Dict[str, Any]) -> bool:
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

        version = Version(protocol=protocol, name=data["version"]["name"])
        players = [
            Player(uuid=player_data["id"], username=player_data["name"])
            for player_data in data["players"]["sample"]
        ]

        ip: str = ip_address
        description = f"{data['description']['text']!a}"
        online = f"{data['players']['online']!a}"
        maximum = f"{data['players']['max']!a}"
        favicon: str = data["favicon"]

        server = Server(
            address=ip,
            version=version,
            players=players,
            description=description,
            online_players=online,
            max_players=maximum,
            favicon=favicon,
            versionProtocol=protocol,
        )
        data = server.dict()
        console.log(data)
        console.log(dir(server.prisma()))

        # await Server.prisma().create(data=data)

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
asyncio.run(d.add_server("123", data))
