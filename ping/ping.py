from mcstatus import JavaServer
from typing import Dict, List


class Ping:
    def __init__(self):
        ...

    async def ping(
        self, ip_address, port: int
    ) -> dict[str, str | int | Dict[str, str | int | list]] | Exception:
        try:
            data = await JavaServer(host=ip_address, port=port).async_status()
            data = data.raw
            """
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
        except Exception as exc:
            data = exc
        return data
