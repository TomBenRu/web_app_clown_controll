import uvicorn
from fastapi import FastAPI

from routers import websocket, department

app = FastAPI()

app.include_router(websocket.router)
app.include_router(department.router)


def run():
    uvicorn.run(app)


if __name__ == '__main__':
    run()
