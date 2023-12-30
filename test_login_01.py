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


if __name__ == '__main__':
    uvicorn.run(app, port=8000)
