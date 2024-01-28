from datetime import datetime, timedelta
from flask import Flask, render_template
from cv2 import VideoCapture, QRCodeDetector
import os

app = Flask(__name__)


def scanQR():
    qcd = QRCodeDetector()
    cap = VideoCapture(0)
    starttime = datetime.now()
    while True:
        if datetime.now()-starttime > timedelta(minutes=2):
            break
        ret, frame = cap.read()

        if ret:
            ret_qr, decoded_info, points, _ = qcd.detectAndDecodeMulti(frame)
            if ret_qr:
                for s, p in zip(decoded_info, points):
                    if s:
                        print(s)
                        return s
    return "Refresh"


@app.route("/", methods=["GET"])
def kiosk():
    return render_template("Kiosk.html")


@app.route("/ScanQR")
def getPDF():
    a = scanQR()
    if a == "Refresh":
        return kiosk()


if __name__ == "__main__":
    app.run(debug=True)
