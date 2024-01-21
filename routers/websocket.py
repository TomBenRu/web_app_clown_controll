import json
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from database import db_services, schemas
from database.enums import AuthorizationTypes
from oaut2_authentication import authentication
from routers.connection_manager import manager, MessageHandler

router = APIRouter(tags=['Web-Socket'])


@router.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):  # todo: user muss sich mit AuthorizationType anmelden

    token = websocket.cookies['clown-call-auth']
    team_of_actors: schemas.TeamOfActorsShow | None = None
    location_id: UUID | None = None
    try:
        token_data = authentication.verify_access_token(AuthorizationTypes.department, token)
        location_id = db_services.Department.get(token_data.id).location.id
    except Exception as e:
        try:
            token_data = authentication.verify_access_token(AuthorizationTypes.actor, token)
            team_of_actors_id = websocket.headers.get("team_of_actors_id")
            team_of_actors = db_services.Actor.get_team_of_actors(team_of_actors_id)
            location_id = team_of_actors.location.id
        except Exception as e:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    await MessageHandler.user_joined_message(token_data, websocket, team_of_actors, location_id)
    try:
        while True:
            data = await websocket.receive_text()
            print(f'{token=}')
            print(f'{json.loads(data)=}')
            message = json.loads(data)['chat-message']
            if message == f'{token}: closing':
                message = 'Wir verabschieden uns für heute. Danke für die Unterstützung!'
            await MessageHandler.handle_message(message, websocket, token_data, team_of_actors, location_id)
    except WebSocketDisconnect as e:
        await MessageHandler.user_leave_message(token_data, websocket, team_of_actors, location_id)
