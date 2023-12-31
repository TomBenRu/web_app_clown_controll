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


class MessageHandler:
    @staticmethod
    async def handle_personal_clown_request_message(data: str, websocket: WebSocket):
        message = f'You wrote: {data}'
        await manager.send_personal_message(message, websocket)

    @staticmethod
    async def handle_broadcast_clown_request_message(data: str, client_id: int, websocket: WebSocket):
        message = f'Client {client_id} says: {data}'
        await manager.broadcast(message, websocket)

    @staticmethod
    async def handle_client_leave(client_id: int, websocket: WebSocket):
        message = f'Client #{client_id} left the chat'
        await manager.broadcast(message, websocket)
