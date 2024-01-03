import uvicorn
from fastapi import FastAPI

from database import db
from routers import websocket, department, auth

app = FastAPI()

app.include_router(websocket.router)
app.include_router(auth.router)
app.include_router(department.router)

db.start_db()


def run():
    uvicorn.run(app)


if __name__ == '__main__':
    run()
