import datetime

from fastapi import FastAPI, Request, Header, WebSocket, WebSocketDisconnect, Query
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
    return templates.TemplateResponse('index2.html.j2', context={'request': request, 'films': films, 'token': '56789'})


@app.websocket('/ws/notifications/')
async def websocket_endpoint(websocket: WebSocket, token: str = Query()):
    print(f'{token=}')
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            print(f'{data=}')
            user_id = data['user-id']
            await websocket.send_text(f"""
            <form id="form" ws-send>
                <div><input  class="hidden" name="user-id" value="1234"><input  class="bg-green-300" name="chat-message"></div>
                <div><button class="bg-blue-300 shadow-lg" ws-send>send</button></div>
            </form>
            <div id="notifications" hx-swap-oob="afterbegin">
                <p>{datetime.datetime.now(): %d.%m.%y %H:%M:%S}: Neue Nachricht von ws to {user_id}.</p>
            </div>""")
    except WebSocketDisconnect:
        print('Client is disconnected')
