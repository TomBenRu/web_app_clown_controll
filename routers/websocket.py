import json

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
    try:
        token_data = authentication.verify_access_token(AuthorizationTypes.department, token)
    except Exception as e:
        try:
            token_data = authentication.verify_access_token(AuthorizationTypes.actor, token)
            team_of_actors_id = websocket.headers.get("team_of_actors_id")
            team_of_actors = db_services.Actor.get_team_of_actors(team_of_actors_id)
        except Exception as e:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    print(f'{token_data=}')

    await MessageHandler.user_joined_message(token_data, websocket, team_of_actors)
    try:
        while True:
            data = await websocket.receive_text()
            print(f'{token=}')
            print(f'{json.loads(data)=}')
            message = json.loads(data)['chat-message']
            await MessageHandler.handle_message(message, websocket, token_data, team_of_actors)
    except WebSocketDisconnect as e:
        await MessageHandler.user_leave_message(token_data, websocket, team_of_actors)
