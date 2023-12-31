from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket, client_id):
        await websocket.accept()
        self.active_connections.append(websocket)
        await self.broadcast(f'{client_id} has joined.', websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, original_websocket: WebSocket):
        for connection in self.active_connections:
            if connection == original_websocket:
                continue
            await connection.send_text(message)


manager = ConnectionManager()
