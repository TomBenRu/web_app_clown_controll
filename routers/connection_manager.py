import datetime

from fastapi import WebSocket
from fastapi.templating import Jinja2Templates

from database import schemas, db_services

templates = Jinja2Templates('templates')


class ConnectionManager:
    def __init__(self):
        self.active_department_connections: list[WebSocket] = []
        self.active_clowns_teams_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket, department: bool):
        await websocket.accept()
        if department:
            self.active_department_connections.append(websocket)
            print(f'-------------------------------------------------------------{self.active_department_connections=}')
        else:
            self.active_clowns_teams_connections.append(websocket)
            print(f'-----------------------------------------------------------{self.active_clowns_teams_connections=}')

    def disconnect(self, websocket: WebSocket, department: bool):
        if department:
            self.active_department_connections.remove(websocket)
            print(f'-------------------------------------------------------------{self.active_department_connections=}')
        else:
            self.active_clowns_teams_connections.remove(websocket)
            print(f'-----------------------------------------------------------{self.active_clowns_teams_connections=}')

    async def send_personal_department_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_personal_clowns_team_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast_departments(self, message: str, original_websocket: WebSocket):
        for connection in self.active_department_connections:
            await connection.send_text(message)

    async def broadcast_clowns_teams(self, message: str, original_websocket: WebSocket):
        for connection in self.active_clowns_teams_connections:
            await connection.send_text(message)

    async def send_alert_to_departments(self, websocket: WebSocket, message: str):
        for ws in self.active_department_connections:
            await ws.send_text(message)

    async def send_alert_to_clown_teams(self, websocket: WebSocket, message: str):
        for ws in self.active_clowns_teams_connections:
            await ws.send_text(message)


manager = ConnectionManager()


class MessageHandler:
    @staticmethod
    async def handle_message(data: str, websocket: WebSocket, token_data: schemas.TokenData):
        now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=1), 'Europe/Berlin')).strftime('%H:%M:%S')
        user = db_services.User.get(token_data.id)
        print(f'{token_data=}')
        if 'department' in token_data.authorizations:
            message_broadcast = f'{user.name} sending: {data}'
            empty_input = templates.get_template('responses/empty_message_input.html').render()
            message_personal = templates.get_template('responses/clown_call_message.html.j2').render(time=now, message=data)
            await manager.broadcast_clowns_teams(message_broadcast, websocket)
            await manager.send_personal_department_message(message_personal, websocket)
            await manager.send_personal_department_message(empty_input, websocket)
        else:
            message_broadcast = templates.get_template('responses/clown_response.html.j2').render(time=now, message=data)
            alert_message_rsv = templates.get_template('responses/alert_message_received.html').render(team=f'Clowns-Team {user.artist_name}')
            message_personal = f'You sent: {data}'
            await manager.broadcast_departments(alert_message_rsv, websocket)
            await manager.broadcast_departments(message_broadcast, websocket)
            await manager.send_personal_clowns_team_message(message_personal, websocket)

    @staticmethod
    async def user_joined_message(token_data: schemas.TokenData, websocket: WebSocket):
        user = db_services.User.get(token_data.id)
        if 'department' in token_data.authorizations:
            await manager.connect(websocket, True)
            message = f'{user.name} has just joined.'
            await manager.send_alert_to_clown_teams(websocket, message)
        else:
            await manager.connect(websocket, False)
            message = templates.get_template('responses/alert_clowns_team_joined.html.j2').render(team=f'Clowns-Team {user.artist_name}')
            await manager.send_alert_to_departments(websocket, message)

    @staticmethod
    async def user_leave_message(token_data: schemas.TokenData, websocket):
        user = db_services.User.get(token_data.id)
        if 'department' in token_data.authorizations:
            message = f'{user.name} has just left.'
            await manager.send_alert_to_clown_teams(websocket, message)
            manager.disconnect(websocket, True)
        else:
            message = templates.get_template('responses/alert_clowns_team_left.html.j2').render(team=f'Clowns-Team {user.artist_name}')
            await manager.send_alert_to_departments(websocket, message)
            manager.disconnect(websocket, False)

