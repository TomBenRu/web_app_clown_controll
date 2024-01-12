import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from routers.connection_manager import manager, MessageHandler

router = APIRouter(tags=['Web-Socket'])


@router.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.cookies['ws-cookie']
    await manager.connect(websocket, department=(token == 'department-token'))
    # await MessageHandler.clown_team_joined_message_to_department(token, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f'{token=}')
            print(f'{json.loads(data)=}')
            message = json.loads(data)['chat-message']
            await MessageHandler.handle_personal_clown_request_message(message, websocket)
            await MessageHandler.handle_broadcast_clown_request_message(message, token, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket, token == 'department-token')
        await MessageHandler.clown_team_leave_message_to_department(token, websocket)
