import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from database import db
from routers import websocket, department, auth, super_user, admin, index, actors, connection_test

app = FastAPI()
static_files = StaticFiles(directory="static")
app.mount("/static", static_files, name="static")

app.include_router(websocket.router)
app.include_router(auth.router)
app.include_router(department.router)
app.include_router(super_user.router)
app.include_router(admin.router)
app.include_router(index.router)
app.include_router(actors.router)
app.include_router(connection_test.router)

db.start_db()


def run():
    uvicorn.run(app)


if __name__ == '__main__':
    run()
