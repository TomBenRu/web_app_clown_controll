import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()


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
    uvicorn.run(app, port=8001)
