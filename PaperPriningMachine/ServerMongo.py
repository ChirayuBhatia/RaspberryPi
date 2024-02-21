from flask import render_template, request, Flask, send_file
from flask_sqlalchemy import SQLAlchemy
import qrcode
from io import BytesIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class Files(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    fid = db.Column(db.String, nullable=False)
    count = db.Column(db.Integer, nullable=False)
    extension = db.Column(db.String, nullable=False)
    file = db.Column(db.LargeBinary, nullable=False)


# with app.app_context():
#     db.drop_all()
#     db.create_all()
#     db.session.commit()


@app.route('/')
def main():
    return render_template("Website.html")


def generate_qr_code(data):
    # Generate QR code image
    img = qrcode.make(data)
    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)
    return buffer


@app.route('/get_qr_code/<int:pdf_id>')
def get_qr_code(pdf_id):
    qr_code_data = f'{pdf_id}'
    qr_code_image = generate_qr_code(qr_code_data)
    return send_file(qr_code_image, mimetype='image/png')


@app.route('/uploadFiles', methods=['POST'])
def success():
    if request.method == 'POST':
        files = request.files.getlist('files[]')
        sno = Files.query.count()
        fid = '1' if sno == 0 else str(int(Files.query.get(sno).fid)+1)
        count = len(files)
        for f in files:
            sno += 1
            count -= 1
            db.session.add(Files(sno=sno, fid=fid, count=count, file=f.read(), extension=f.filename.rsplit('.')[-1]))
        db.session.commit()
        qr_code_url = f'/get_qr_code/{fid}'
        return render_template("Acknowledgement.html", name="File", qr_code_url=qr_code_url)


@app.route('/checkqr', methods=['POST'])
def checkqr():
    try:
        fid = eval(request.args.get('text'))["fid"]
        res = Files.query.filter_by(fid=fid).count()
        print(res)
        if res:
            return {"fid": fid, "count": res}
        else:
            return "Invalid"
    except:
        return "Invalid"


@app.route('/get_file', methods=['GET'])
def get_files():
    fid = request.args.get("fid")
    count = request.args.get("count")
    print(fid, count)
    pdf_entry = Files.query.filter_by(fid=fid, count=count).first()
    return send_file(BytesIO(pdf_entry.file), as_attachment=True, download_name=pdf_entry.extension)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
