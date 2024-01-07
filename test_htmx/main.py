import datetime

from fastapi import FastAPI, Request, Header, WebSocket, WebSocketDisconnect
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
    return templates.TemplateResponse('index2.html.j2', context={'request': request, 'films': films})


@app.websocket('/ws/notifications/')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            print(f'{data["chat-message"]=}')
            await websocket.send_text(f"""
            <form id="form" ws-send>
                <input name="chat-message">
            </form>
            <div id="notifications" hx-swap-oob="afterbegin">
                <p>{datetime.datetime.now(): %d.%m.%y %H:%M:%S}: Neue Nachricht von ws.</p>
            </div>""")
    except WebSocketDisconnect:
        print('Client is disconnected')
