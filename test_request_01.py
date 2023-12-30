import httpx
import asyncio

async def main():
    async with httpx.AsyncClient() as client:
        while True:
            username = input('username: ')
            password = input('password: ')
            response = await client.post('http://127.0.0.1:8000/login/',
                                         json={'username': username, 'password': password})
            print(response.json())

# asyncio.run() ist verfügbar ab Python 3.7
# Wenn Sie eine ältere Version von Python verwenden, müssen Sie einen Event-Loop erstellen und diesen Task darin ausführen.
asyncio.run(main())
