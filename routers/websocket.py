import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from routers.connection_manager import manager, MessageHandler

router = APIRouter(tags=['Web-Socket'])


@router.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.cookies['ws-cookie']
    await MessageHandler.user_joined_message(token, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f'{token=}')
            print(f'{json.loads(data)=}')
            message = json.loads(data)['chat-message']
            await MessageHandler.handle_message(message, websocket, token)
    except WebSocketDisconnect as e:
        print(f'Exception: {e}')
        manager.disconnect(websocket, token == 'department-token')
        await MessageHandler.user_leave_message(token, websocket)
