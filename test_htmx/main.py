import datetime
import time

from fastapi import FastAPI, Request, Header, WebSocket, WebSocketDisconnect, Query, Cookie
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


app = FastAPI()
templates = Jinja2Templates('templates')


class MessageHandler:
    @staticmethod
    async def send_to_remote(websocket: WebSocket, message: str):
        message_text = (f"Message from server at {datetime.datetime.now().strftime('%d.%m.%y %H:%M:%S')} to "
                        f"{websocket.cookies}: {message}")
        await websocket.send_text(message_text)

    @staticmethod
    async def send_to_web_client(websocket: WebSocket, message: str):
        message_text = templates.get_template('server_ws_response.html.j2').render(
            curr_time=datetime.datetime.now().strftime('%d.%m.%y %H:%M:%S'), sender=websocket.cookies,
            message=message)
        await websocket.send_text(message_text)

    @staticmethod
    async def send_message(websocket: WebSocket, message: str):
        if websocket.cookies.get('ws-cookie') == 'clown-team-token':
            await MessageHandler.send_to_remote(websocket, message)
        else:
            await MessageHandler.send_to_web_client(websocket, message)


@app.get('/index/', response_class=HTMLResponse)
def index(request: Request, hx_request: str | None = Header(default=None)):
    films = [
        {'name': 'Blade Runner', 'director': 'Ridley Scott'},
        {'name': 'Pulp Fiction', 'director': 'Quentin Tarantino'},
        {'name': 'Mulholland Drive', 'director': 'David Lynch'}
    ]
    if hx_request:
        return
    response = templates.TemplateResponse('index2.html.j2', context={'request': request, 'films': films})
    response.set_cookie(key='ws-cookie', value='department-token')
    return response


@app.websocket('/ws/notifications/')
async def websocket_endpoint(websocket: WebSocket):
    print('------------------------in---------------------------')
    await websocket.accept()
    # token = websocket.cookies['ws-cookie']
    token = websocket.cookies['ws-cookie']
    print(f'{websocket.headers=}')
    # print(f'{websocket.cookies=}')
    try:
        while True:
            data = await websocket.receive_json()
            print(f'{data=}')
            await MessageHandler.send_message(websocket, 'Wie geht es dir?')
    except WebSocketDisconnect:
        print('Client is disconnected')
