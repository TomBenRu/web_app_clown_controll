import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from database.enums import AuthorizationTypes
from oaut2_authentication import authentication
from routers.connection_manager import manager, MessageHandler

router = APIRouter(tags=['Web-Socket'])


@router.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):  # todo: user muss sich mit AuthorizationType anmelden
    token = websocket.cookies['clown-call-auth']
    print(f'{token=}')
    try:
        token_data = authentication.verify_access_token(AuthorizationTypes.department, token)
    except Exception as e:
        try:
            token_data = authentication.verify_access_token(AuthorizationTypes.actor, token)
        except Exception as e:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    print(f'{token_data=}')

    await MessageHandler.user_joined_message(token_data, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f'{token=}')
            print(f'{json.loads(data)=}')
            message = json.loads(data)['chat-message']
            await MessageHandler.handle_message(message, websocket, token_data)
    except WebSocketDisconnect as e:
        print(f'Exception: {e}')
        await MessageHandler.user_leave_message(token_data, websocket)
