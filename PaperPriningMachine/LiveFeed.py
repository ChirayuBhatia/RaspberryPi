from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import cv2
import base64

app = Flask(__name__)
socketio = SocketIO(app)
camera = cv2.VideoCapture(0)


def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            _, buffer = cv2.imencode('.jpg', frame)
            frame_data = base64.b64encode(buffer).decode('utf-8')
            socketio.emit('image', frame_data)
            socketio.sleep(0.1)


@app.route('/')
def index():
    return render_template('CameraFeed.html')


@socketio.on('connect')
def handle_connect():
    print('Client connected')
    socketio.start_background_task(target=generate_frames)


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
