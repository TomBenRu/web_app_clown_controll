import datetime
import json
from collections import defaultdict
from uuid import UUID

from fastapi import WebSocket
from fastapi.templating import Jinja2Templates

from database import schemas, db_services

templates = Jinja2Templates('templates')


class ConnectionManager:
    def __init__(self):
        self.active_department_connections: defaultdict[UUID, list] = defaultdict(list)
        self.active_clowns_teams_connections: defaultdict[UUID, list] = defaultdict(list)

    async def connect(self, websocket: WebSocket, department: bool, location_id: UUID):
        await websocket.accept()
        if department:
            self.active_department_connections[location_id].append(websocket)
            print(f'{self.active_department_connections=}')
        else:
            self.active_clowns_teams_connections[location_id].append(websocket)
            print(f'{self.active_clowns_teams_connections=}')

    def disconnect(self, websocket: WebSocket, department: bool, location_id: UUID):
        if department:
            self.active_department_connections[location_id].remove(websocket)
            print(f'{self.active_department_connections=}')
        else:
            self.active_clowns_teams_connections[location_id].remove(websocket)
            print(f'{self.active_clowns_teams_connections=}')

    async def send_personal_department_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_personal_clowns_team_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast_departments(self, message: str, original_websocket: WebSocket, location_id: UUID):
        for connection in self.active_department_connections[location_id]:
            await connection.send_text(message)

    async def broadcast_clowns_teams(self, message: str, original_websocket: WebSocket, location_id: UUID):
        for connection in self.active_clowns_teams_connections[location_id]:
            await connection.send_text(message)

    async def send_alert_to_departments(self, websocket: WebSocket, message: str, location_id: UUID):
        print(f'{websocket.headers=}')
        for ws in self.active_department_connections[location_id]:
            print(f'{ws.headers=}')
            await ws.send_text(message)

    async def send_alert_to_clown_teams(self, websocket: WebSocket, message: str, location_id: UUID):
        for ws in self.active_clowns_teams_connections[location_id]:
            await ws.send_text(message)


manager = ConnectionManager()


class MessageHandler:
    @staticmethod
    async def handle_message(data: str, websocket: WebSocket, token_data: schemas.TokenData,
                             team_of_actors: schemas.TeamOfActorsShow | None, location_id: UUID):
        now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=1),
                                                         'Europe/Berlin')).strftime('%H:%M:%S')
        user = db_services.User.get(token_data.id)
        if 'department' in token_data.authorizations:
            message_broadcast = json.dumps({'sender_id': str(token_data.id), 'message': data, 'time': str(datetime.datetime.now())})
            empty_input = templates.get_template('responses/empty_message_input.html').render()
            message_personal = templates.get_template('responses/clown_call_message.html.j2').render(
                time=now, message=data)
            await manager.broadcast_clowns_teams(message_broadcast, websocket, location_id)
            await manager.send_personal_department_message(message_personal, websocket)
            await manager.send_personal_department_message(empty_input, websocket)
        else:
            actors = ', '.join([a.artist_name for a in team_of_actors.actors])
            message_broadcast = templates.get_template('responses/clown_response.html.j2').render(
                time=now, message=data, clowns_team=actors)
            alert_message_rsv = templates.get_template(
                'responses/alert_message_received.html').render(team=f'Clowns-Team: {actors}')
            message_personal = json.dumps({'send_confirmation': data})
            await manager.broadcast_departments(alert_message_rsv, websocket, location_id)
            await manager.broadcast_departments(message_broadcast, websocket, location_id)
            await manager.send_personal_clowns_team_message(message_personal, websocket)

    @staticmethod
    async def user_joined_message(token_data: schemas.TokenData, websocket: WebSocket,
                                  team_of_actors: schemas.TeamOfActorsShow | None, location_id: UUID):
        user = db_services.User.get(token_data.id)
        if 'department' in token_data.authorizations:
            await manager.connect(websocket, True, location_id)
            message = json.dumps({'sender_id': str(token_data.id), 'joined': True, 'time': str(datetime.datetime.now())})
            await manager.send_alert_to_clown_teams(websocket, message, location_id)
        else:
            await manager.connect(websocket, False, location_id)
            actors = ', '.join([a.artist_name for a in team_of_actors.actors])
            message = templates.get_template('responses/alert_clowns_team_joined.html.j2').render(team=f'Clowns-Team: {actors}')
            await manager.send_alert_to_departments(websocket, message, location_id)

    @staticmethod
    async def user_leave_message(token_data: schemas.TokenData, websocket,
                                 team_of_actors: schemas.TeamOfActorsShow | None, location_id: UUID):
        user = db_services.User.get(token_data.id)
        if 'department' in token_data.authorizations:
            message = json.dumps({'sender_id': str(token_data.id), 'left': True, 'time': str(datetime.datetime.now())})
            await manager.send_alert_to_clown_teams(websocket, message, location_id)
            manager.disconnect(websocket, True, location_id)
        else:
            actors = ', '.join([a.artist_name for a in team_of_actors.actors])

            message = templates.get_template('responses/alert_clowns_team_left.html.j2').render(team=f'Clowns-Team: {actors}')
            await manager.send_alert_to_departments(websocket, message, location_id)
            manager.disconnect(websocket, False, location_id)

