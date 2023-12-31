from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.connection_manager import manager, MessageHandler

router = APIRouter(tags=['Web-Socket'])


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            await MessageHandler.handle_personal_clown_request_message(data, websocket)
            await MessageHandler.handle_broadcast_clown_request_message(data, client_id, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await MessageHandler.handle_client_leave(client_id, websocket)
