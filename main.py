from datetime import datetime
from dataclasses import dataclass, asdict
from flask import Flask, request
from flask_socketio import SocketIO, emit
import threading

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

@dataclass
class Client:
    client_id: str
    connection_start: datetime

clients = {}


@socketio.on("message")
def handle_message(data):
    print("received message: " + data)


@socketio.on("disconnect")
def handle_message():
    with threading.Lock():
        global clients
        client: Client = clients.pop(request.sid)
        print("client left ", asdict(client))
        print("total clients: ", len(clients))


@socketio.on("connect")
def handle_message():
    with threading.Lock():
        global clients
        clients[request.sid] = Client(
            client_id=request.sid,
            connection_start=datetime.now(),
        )
        print("new client ", asdict(clients[request.sid]))
        print("total clients: ", len(clients))


@socketio.event
def timestamp():
    emit('timestamp', datetime.now().isoformat())


@socketio.event
def total_clients():
    global clients
    emit('total_clients', len(clients))


@socketio.event
def age():
    global clients
    emit('age', str(datetime.now() - clients[request.sid].connection_start))


def send_heart_beat():
    while True:
        print("Sending heart beat...")
        socketio.emit("heart_beat", "Connected", broadcast=True)
        socketio.sleep(seconds=60)


if __name__ == "__main__":
    socketio.start_background_task(send_heart_beat)
    socketio.run(app)
