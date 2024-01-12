import uvicorn
from fastapi import FastAPI

from database import db
from routers import websocket, department, auth, super_user, admin, index

app = FastAPI()

app.include_router(websocket.router)
app.include_router(auth.router)
app.include_router(department.router)
app.include_router(super_user.router)
app.include_router(admin.router)
app.include_router(index.router)

db.start_db()


def run():
    uvicorn.run(app)


if __name__ == '__main__':
    run()
