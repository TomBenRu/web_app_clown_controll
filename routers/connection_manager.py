import datetime

from fastapi import WebSocket
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates('templates')


class ConnectionManager:
    def __init__(self):
        self.active_department_connections: list[WebSocket] = []
        self.active_clowns_teams_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket, department: bool):
        await websocket.accept()
        if department:
            self.active_department_connections.append(websocket)
        else:
            self.active_clowns_teams_connections.append(websocket)

    def disconnect(self, websocket: WebSocket, department: bool):
        self.active_department_connections.remove(websocket)

    async def send_personal_department_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, original_websocket: WebSocket, departments: bool, clown_teams: bool):
        for connection in self.active_department_connections:
            if connection == original_websocket:
                continue
            await connection.send_text(message)


manager = ConnectionManager()


class MessageHandler:
    @staticmethod
    async def handle_personal_clown_request_message(data: str, websocket: WebSocket):
        now = datetime.datetime.now().strftime('%H:%M:%S')
        message = templates.get_template('responses/clown_call_message.html.j2').render(time=now, message=data)
        await manager.send_personal_department_message(message, websocket)

    @staticmethod
    async def handle_broadcast_clown_request_message(data: str, token: str, websocket: WebSocket):
        message = f'Department {token} says: {data}'
        await manager.broadcast(message, websocket, departments=False, clown_teams=True)

    @staticmethod
    async def clown_team_joined_message_to_department(token: str, websocket: WebSocket):
        message = templates.get_template('responses/clowns_team_joined').render(team=token)
        await manager.broadcast(message, websocket)

    @staticmethod
    async def clown_team_leave_message_to_department(token: str, websocket: WebSocket):
        message = templates.get_template('responses/clowns_team_leave').render(team=token)
        await manager.broadcast(message, websocket)
