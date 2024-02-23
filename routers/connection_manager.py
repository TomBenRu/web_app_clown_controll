import datetime
import json
import uuid
from collections import defaultdict
from uuid import UUID

from fastapi import WebSocket
from fastapi.templating import Jinja2Templates

from commands import cmd_actor
from database import schemas, db_services
from database.enums import AuthorizationTypes
from oaut2_authentication import authentication

templates = Jinja2Templates('templates')


class ConnectionManager:
    def __init__(self):
        self.active_department_connections: defaultdict[UUID, set[WebSocket]] = defaultdict(set)
        self.active_clowns_teams_connections: defaultdict[UUID, set[WebSocket]] = defaultdict(set)
        self.disconnected_clowns_teams: defaultdict[UUID, set[str]] = defaultdict(set)

    async def connect(self, websocket: WebSocket, department: bool, location_id: UUID):
        print('............................. in connect', flush=True)
        await websocket.accept()
        if department:
            self.active_department_connections[location_id].add(websocket)
        else:
            # bei schnellen Verbindungsabbrüchen und -wiederherstellungen können Verdoppelungen auftreten,
            # daher wird hier geprüft, ob die Verbindung mit team_of_actors_id bereits vorhanden ist
            connections_to_remove = set()
            for con in self.active_clowns_teams_connections[location_id]:
                if con.headers.get("team_of_actors_id") == websocket.headers.get("team_of_actors_id"):
                    connections_to_remove.add(con)
            self.active_clowns_teams_connections[location_id] -= connections_to_remove
            self.active_clowns_teams_connections[location_id].add(websocket)
            if (t_of_a_id := websocket.headers.get("team_of_actors_id")) in self.disconnected_clowns_teams[location_id]:
                self.disconnected_clowns_teams[location_id].remove(t_of_a_id)
                if not self.disconnected_clowns_teams[location_id]:
                    del self.disconnected_clowns_teams[location_id]

            await self.send_pending_clowns_team_messages(websocket)
        print(f'........................... {dict(self.active_department_connections)=}', flush=True)
        print(f'........................... {dict(self.active_clowns_teams_connections)=}', flush=True)
        print(f'........................... {dict(self.disconnected_clowns_teams)=}', flush=True)

    def disconnect(self, websocket: WebSocket, department: bool, location_id: UUID, connection_lost: bool):
        print(f'in manager.disconnect().......................... {websocket=}, {department=}, {connection_lost=}',
              flush=True)
        if department:
            self.active_department_connections[location_id].remove(websocket)
            print(f'.................................................{self.active_department_connections=}')
        else:
            if websocket in self.active_clowns_teams_connections[location_id]:  # kann schon in connect() entfernt worden sein
                self.active_clowns_teams_connections[location_id].remove(websocket)
            if connection_lost:
                self.disconnected_clowns_teams[location_id].add(websocket.headers.get("team_of_actors_id"))
            else:
                cmd_actor.DeleteTeamOfActors(UUID(websocket.headers.get("team_of_actors_id"))).execute()

    async def send_pending_clowns_team_messages(self, websocket: WebSocket):
        return
        print('in send_pending_clowns_team_messages', flush=True)
        team_of_actors_id = UUID(websocket.headers.get('team_of_actors_id'))
        pending_messages = db_services.Actor.get_all_session_messages_of_team_of_actors(team_of_actors_id, True)
        for session_message in pending_messages:
            await self.send_personal_clowns_team_message(session_message.message, websocket, False)

    async def send_personal_department_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_personal_clowns_team_message(self, message: str, websocket: WebSocket, first_try: bool = True):
        if first_try:
            db_services.Actor.create_session_message(
                schemas.SessionMessageCreate(message=message,
                                             sent=None,
                                             team_of_actors_id=UUID(websocket.headers.get("team_of_actors_id"))))
        await websocket.send_text(message)

    async def broadcast_departments(self, message: str, original_websocket: WebSocket, location_id: UUID, receiver_id: str | None):
        for ws in self.active_department_connections[location_id]:
            if receiver_id:
                token = ws.cookies['clown-call-auth']
                token_data = authentication.verify_access_token(AuthorizationTypes.department, token)
                if str(token_data.id) == receiver_id:
                    await ws.send_text(message)
                    return
            else:
                await ws.send_text(message)

    async def broadcast_clowns_teams(self, message: dict, original_websocket: WebSocket, location_id: UUID):
        for connection in self.active_clowns_teams_connections[location_id]:
            message_id = str(uuid.uuid4())
            message_with_id = json.dumps(message | {'message_id': message_id})
            print(f'in broadcast_clowns_teams()............................ {message_with_id=}', flush=True)
            db_services.Actor.create_session_message(
                schemas.SessionMessageCreate(message=message_with_id,
                                             sent=None,
                                             team_of_actors_id=UUID(connection.headers.get("team_of_actors_id"))))
            await connection.send_text(message_with_id)

    async def send_alert_to_departments(self, websocket: WebSocket, message: str, location_id: UUID):
        print('..................................... in send_alert_to_departments', flush=True)
        print(f'..................................... {self.active_department_connections=}', flush=True)
        print(f'...................................... {location_id=}', flush=True)
        for ws in self.active_department_connections[location_id]:
            print(f'....................................... send to {ws=}', flush=True)
            await ws.send_text(message)

    async def send_alert_to_clown_teams(self, websocket: WebSocket, message: dict, location_id: UUID):
        for ws in self.active_clowns_teams_connections[location_id]:
            message_id = str(uuid.uuid4())
            message_with_id = json.dumps(message | {'message_id': message_id})
            print(f'in broadcast_clowns_teams()............................ {message_with_id=}', flush=True)
            db_services.Actor.create_session_message(
                schemas.SessionMessageCreate(message=message_with_id,
                                             sent=None,
                                             team_of_actors_id=UUID(ws.headers.get("team_of_actors_id"))))
            await ws.send_text(message_with_id)

    async def send_personal_clowns_team_message_departments_joined(self, websocket: WebSocket, location_id: UUID,
                                                                   message_id: str, time: str, reconnect: bool):
        for ws in self.active_department_connections[location_id]:
            token = ws.cookies['clown-call-auth']
            token_data = authentication.verify_access_token(AuthorizationTypes.department, token)
            message = json.dumps({'department_id': str(token_data.id), 'joined': True,
                                  'time': str(datetime.datetime.now()), 'reconnect': reconnect,
                                  'message_id': message_id})
            db_services.Actor.create_session_message(
                schemas.SessionMessageCreate(message=message,
                                             sent=None,
                                             team_of_actors_id=UUID(websocket.headers.get("team_of_actors_id"))))
            await websocket.send_text(message)


manager = ConnectionManager()


def get_text_clowns_teams_online_offline(location_id: UUID) -> tuple[str, str]:
    # sourcery skip: use-named-expression
    teams_online = ([db_services.Actor.get_team_of_actors(UUID(ws.headers['team_of_actors_id']))
                     for ws in manager.active_clowns_teams_connections[location_id]])
    if teams_online:
        text_teams_online = ' | '.join([f'''Team "{', '.join([a.artist_name for a in t.actors])}"'''
                                        for t in teams_online]) + ' (online)'
    else:
        text_teams_online = ''

    # Falls die Remote-App on ausloggen geschlossen wurde,
    # kann durch erneutes Einloggen in der Location der Team-Status zurückgesetzt werden:
    if disconnected_team_ids := manager.disconnected_clowns_teams[location_id]:
        disconnected_team_ids = {team_id for team_id in disconnected_team_ids
                                 if db_services.Actor.get_team_of_actors(UUID(team_id))}
        if not disconnected_team_ids:
            del manager.disconnected_clowns_teams[location_id]

    if disconnected_team_ids:
        disconnected_clowns_teams = [db_services.Actor.get_team_of_actors(UUID(team_id))
                                     for team_id in manager.disconnected_clowns_teams[location_id]]
        text_teams_offline = ' | '.join([f'''Team "{', '.join([a.artist_name for a in t.actors])}"'''
                                         for t in disconnected_clowns_teams]) + ' (offline)'
    else:
        text_teams_offline = ''

    if not text_teams_online and not text_teams_offline:
        text_teams_offline = 'Kein Clowns-Team.'

    return text_teams_online, text_teams_offline


class MessageHandler:
    @staticmethod
    async def handle_message(data: str, websocket: WebSocket, token_data: schemas.TokenData,
                             team_of_actors: schemas.TeamOfActorsShow | None, location_id: UUID,
                             receiver_id: str | None, closing: bool = False):
        print('..................................in MessageHandler.handle_message', flush=True)
        now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=1), 'Europe/Berlin'))

        if 'department' in token_data.authorizations:
            message_broadcast = {'department_id': str(token_data.id), 'message': data, 'time': str(now)}
            empty_input = templates.get_template('responses/empty_message_input.html').render()
            message_personal = templates.get_template('responses/clown_call_message.html.j2').render(
                time=now.strftime('%H:%M:%S'), message=data)
            await manager.broadcast_clowns_teams(message_broadcast, websocket, location_id)
            await manager.send_personal_department_message(message_personal, websocket)
            await manager.send_personal_department_message(empty_input, websocket)
        else:
            actors = ', '.join([a.artist_name for a in team_of_actors.actors])
            message_broadcast = templates.get_template('responses/clown_response.html.j2').render(
                time=now.strftime('%H:%M:%S'), message=data, clowns_team=actors)
            alert_message_rsv = templates.get_template(
                'responses/alert_message_received.html').render(team=f'Clowns-Team: {actors}')
            print(f'................................... {alert_message_rsv=}', flush=True)
            message_personal = {'send_confirmation': data, 'time': str(now),
                                'sender_id': websocket.headers.get('team_of_actors_id'),
                                'receiver_id': receiver_id}
            await manager.broadcast_departments(alert_message_rsv, websocket, location_id, receiver_id)
            await manager.broadcast_departments(message_broadcast, websocket, location_id, receiver_id)
            if not closing:
                # await manager.send_personal_clowns_team_message(message_personal, websocket)
                await manager.broadcast_clowns_teams(message_personal, websocket, location_id)

    @staticmethod
    def handle_send_confirmation(confirmation: dict):
        print(f'in handle_send_confirmation...................... {confirmation=}', flush=True)
        db_services.Actor.set_session_message_as_sent(UUID(confirmation['message_id']))

    @staticmethod
    async def user_joined_message(token_data: schemas.TokenData, websocket: WebSocket,
                                  team_of_actors: schemas.TeamOfActorsShow | None, location_id: UUID):
        print('..................................... in user_joined_message', flush=True)
        now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=1), 'Europe/Berlin'))
        user = db_services.User.get(token_data.id)
        if 'department' in token_data.authorizations:
            await manager.connect(websocket, True, location_id)
            message = {'department_id': str(token_data.id), 'joined': True, 'time': str(now)}
            await manager.send_alert_to_clown_teams(websocket, message, location_id)
            text_teams_online, text_teams_offline = get_text_clowns_teams_online_offline(location_id)
            note_presence = (templates.get_template('responses/note_clowns_teams_presence.html.j2')
                             .render(text_teams_online=text_teams_online, text_teams_offline=text_teams_offline))
            await manager.send_personal_department_message(note_presence, websocket)
        else:
            clowns_team_offline = (websocket.headers.get('team_of_actors_id')
                                   in manager.disconnected_clowns_teams[location_id])
            await manager.connect(websocket, False, location_id)
            actors = ', '.join([a.artist_name for a in team_of_actors.actors])

            message_to_departments = (templates.get_template('responses/alert_clowns_team_joined.html.j2')
                                      .render(team=f'Clowns-Team: {actors}'))
            print(f'............................ {message_to_departments=}', flush=True)

            await manager.send_alert_to_departments(websocket, message_to_departments, location_id)
            reconnect = clowns_team_offline
            await manager.send_personal_clowns_team_message_departments_joined(websocket,
                                                                               location_id,
                                                                               str(uuid.uuid4()),
                                                                               str(now),
                                                                               reconnect)

            text_teams_online, text_teams_offline = get_text_clowns_teams_online_offline(location_id)
            note_presence = (templates.get_template('responses/note_clowns_teams_presence.html.j2')
                             .render(text_teams_online=text_teams_online, text_teams_offline=text_teams_offline))
            await manager.broadcast_departments(note_presence, websocket, location_id, None)

    @staticmethod
    async def user_leave_message(token_data: schemas.TokenData, websocket,
                                 team_of_actors: schemas.TeamOfActorsShow | None,
                                 location_id: UUID, connection_lost: bool):
        now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=1), 'Europe/Berlin'))
        user = db_services.User.get(token_data.id)
        if 'department' in token_data.authorizations:
            manager.disconnect(websocket, True, location_id, False)
            message = json.dumps({'department_id': str(token_data.id), 'left': True,
                                  'time': str(now), 'message_id': str(uuid.uuid4())})
            await manager.send_alert_to_clown_teams(websocket, message, location_id)
        else:
            manager.disconnect(websocket, False, location_id, connection_lost)
            actors = ', '.join([a.artist_name for a in team_of_actors.actors])
            if connection_lost:
                message = (templates.get_template('responses/alert_clowns_team_connection_lost.html.j2')
                           .render(team=f'Clowns-Team: {actors}'))
            else:
                message = (templates.get_template('responses/alert_clowns_team_left.html.j2')
                           .render(team=f'Clowns-Team: {actors}'))
            await manager.send_alert_to_departments(websocket, message, location_id)

            text_teams_online, text_teams_offline = get_text_clowns_teams_online_offline(location_id)

            note_presence = (templates.get_template('responses/note_clowns_teams_presence.html.j2')
                             .render(text_teams_online=text_teams_online, text_teams_offline=text_teams_offline))
            await manager.broadcast_departments(note_presence, websocket, location_id, None)
