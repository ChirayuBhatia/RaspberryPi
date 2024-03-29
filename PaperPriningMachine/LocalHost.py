from datetime import datetime, timedelta
from flask import Flask, render_template, request
import cv2
import requests
# from picamera import PiCamera
# from picamera.array import PiRGBArray
import os

app = Flask(__name__)


def scanQR():
    # qcd = cv2.QRCodeDetector()
    # camera = PiCamera()
    # camera.resolution = (640, 480)
    # raw_capture = PiRGBArray(camera, size=(640, 480))
    #
    # starttime = datetime.now()
    #
    # for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
    #     image = frame.array
    #
    #     ret_qr, decoded_info, points, _ = qcd.detectAndDecodeMulti(image)
    #
    #     if ret_qr:
    #         for s, p in zip(decoded_info, points):
    #             if s:
    #                 print(s)
    #
    s = {"fid": '1'}
    res = requests.post(f"http://192.168.168.29:5000/checkqr?text={s}")
    if res.text == "Invalid":
        # continue
        pass
    else:
        return eval(res.text)
    #
    #     raw_capture.truncate(0)  # Clear the stream for the next frame
    #
    #     if datetime.now() - starttime > timedelta(minutes=2):
    #         break
    #
    # return "Refresh"


@app.route("/", methods=["GET"])
def kiosk():
    return render_template("Kiosk.html")


@app.route("/ScanQR")
def getfiles():
    res = scanQR()
    if res == "Refresh":
        return kiosk()
    else:
        return render_template('Printing.html', fid=res["fid"], count=res["count"])


# @app.route("/Print")
# def printing():
#     fid = 6
#     # fid = request.args.get('fid')
#     print("Downloading file...")
#     response = requests.get('http://192.168.224.29:5000/get_file/' + str(fid))
#     if response.status_code == 200:
#         print('File downloaded successfully.')
#         with open('Files/' + str(fid) + ".pdf", 'wb') as f:
#             f.write(response.content)
#         os.system('lp -d HP_LaserJet_P1007_USB_NC0AL8A_HPLIP Files/' + str(fid) + ".pdf")
#         return "File downloaded and saved successfully."
#     else:
#         print('Failed to download file. Status code:', response.status_code)
#         return "Failed to download file."


@app.route("/Print/<fid>/<count>")
def printing(fid, count):
    for x in range(int(count)-1, -1, -1):
        response = requests.get('http://192.168.168.29:5000/get_file?fid='+str(fid)+'&count='+str(x))
        filename = "Files/" + fid + "_" + count + "." + response.headers.get('Content-Disposition').split('=')[1]
        with open(filename, "wb") as f:
            f.write(response.content)
            # os.system('lp -d HP_LaserJet_P1007_USB_NC0AL8A_HPLIP Files/' + filename)
    return "Done"


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)

