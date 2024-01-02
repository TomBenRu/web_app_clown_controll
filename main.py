import uvicorn
from fastapi import FastAPI

from database import db
from routers import websocket, department


db.start_db()

app = FastAPI()

app.include_router(websocket.router)
app.include_router(department.router)


def run():
    uvicorn.run(app)


if __name__ == '__main__':
    run()
