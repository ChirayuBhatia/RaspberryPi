from flask import render_template, request, Flask, send_file
from flask_sqlalchemy import SQLAlchemy
import img2pdf
import docx2pdf
import pypdf
import qrcode
from io import BytesIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class PDF(db.Model):
    id = db.Column(db.String, primary_key=True)
    file = db.Column(db.LargeBinary, nullable=False)


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
        merger = pypdf.PdfMerger()
        for f in files:
            if not f.filename.endswith(".pdf"):
                if f.filename.endswith(".docx") or f.filename.endswith(".doc"):
                    f = docx2pdf.convert(f)
                else:
                    f = img2pdf.convert(f, rotation=img2pdf.Rotation.ifvalid)
                merger.append(BytesIO(f))
            else:
                merger.append(BytesIO(f.read()))
        op = BytesIO()
        merger.write(op)
        op.seek(0)
        pdf_id = PDF.query.count() + 1
        db.session.add(PDF(id=pdf_id, file=op.read()))
        db.session.commit()
        qr_code_url = f'/get_qr_code/{pdf_id}'
        return render_template("Acknowledgement.html", name=[f.filename for f in files],
                               qr_code_url=qr_code_url)


@app.route('/get_file/<fid>', methods=['GET'])
def get_files(fid):
    pdf_entry = PDF.query.get(fid)
    return send_file(BytesIO(pdf_entry.file), as_attachment=True, download_name=f'{fid}.pdf')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
