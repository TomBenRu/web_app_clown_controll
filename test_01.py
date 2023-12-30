import uvicorn
from fastapi import FastAPI, WebSocket, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    username: str
    password: str

logged_in_users = []

@app.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        if logged_in_users:
            await websocket.send_text(f"{logged_in_users[-1]} hat sich angemeldet")
            logged_in_users.pop()

@app.post("/login/")
async def login(user: User):
    # Überprüfen Sie die Anmeldeinformationen hier
    # Wenn die Anmeldeinformationen korrekt sind:
    logged_in_users.append(user.username)
    return {"message": f"{user.username} erfolgreich angemeldet"}

@app.get("/", response_class=HTMLResponse)
async def read_items(request: Request):
    return """
    <html>
        <head>
            <title>FastAPI Websocket Beispiel</title>
        </head>
        <body>
            <h1>Willkommen auf der Webseite!</h1>
            <ul id="users"></ul>
            <script>
                var ws = new WebSocket("ws://localhost:8000/ws/");
                ws.onmessage = function(event) {
                    var users = document.getElementById('users');
                    var user = document.createElement('li');
                    user.textContent = event.data;
                    users.appendChild(user);
                };
                ws.onclose = function(event) {
                    console.log('WebSocket connection closed');
                };
                ws.onerror = function(error) {
                    console.log('WebSocket error: ', error);
                };
                window.onbeforeunload = function() {
                    ws.close();
                };
            </script>
        </body>
    </html>
    """


if __name__ == '__main__':
    uvicorn.run(app)
