import datetime

from fastapi import FastAPI, Request, Header, WebSocket, WebSocketDisconnect, Query, Cookie
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


app = FastAPI()
templates = Jinja2Templates('templates')


@app.get('/index/', response_class=HTMLResponse)
def index(request: Request, hx_request: str | None = Header(default=None)):
    films = [
        {'name': 'Blade Runner', 'director': 'Ridley Scott'},
        {'name': 'Pulp Fiction', 'director': 'Quentin Tarantino'},
        {'name': 'Mulholland Drive', 'director': 'David Lynch'}
    ]
    if hx_request:
        return templates.TemplateResponse('table.html.j2', context={'request': request, 'films': films})
    response = templates.TemplateResponse('index2.html.j2', context={'request': request, 'films': films})
    response.set_cookie(key='ws-cookie', value='my-ws-token')
    return response


@app.websocket('/ws/notifications/')
async def websocket_endpoint(websocket: WebSocket):
    print('------------------------in---------------------------')
    await websocket.accept()
    print(f'{websocket.headers=}')
    print(f'{websocket.cookies=}')
    try:
        while True:
            data = await websocket.receive_json()
            print(f'{data=}')
            await websocket.send_text(f"""
            <form id="form" ws-send>
                <div><input  class="bg-green-300" name="chat-message"></div>
                <div><button class="bg-blue-300 shadow-lg" ws-send>send</button></div>
            </form>
            <div id="notifications" hx-swap-oob="afterbegin">
                <p>{datetime.datetime.now(): %d.%m.%y %H:%M:%S}: Neue Nachricht von ws to {websocket.cookies}.</p>
            </div>""")
    except WebSocketDisconnect:
        print('Client is disconnected')
