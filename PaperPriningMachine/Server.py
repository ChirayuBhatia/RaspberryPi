from flask import render_template, request, Flask, send_file
from flask_sqlalchemy import SQLAlchemy
from zipfile import ZipFile
import img2pdf
import docx2pdf
import pypdf
import qrcode
from io import BytesIO

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://files_nvc9_user:ObFQb0TBnCPjPP4oGy2AR8LmbPJ72JJJ@dpg-cn5qip7109ks73a0c6f0-a.singapore-postgres.render.com/files_nvc9'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class PDF(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String, nullable=False)
    file = db.Column(db.LargeBinary, nullable=False)


# with app.app_context():
#     db.create_all()


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


# @app.route('/uploadFiles', methods=['POST'])
# def success():
#     if request.method == 'POST':
#         files = request.files.getlist('files[]')
#         merger = pypdf.PdfMerger()
#         for f in files:
#             if not f.filename.endswith(".pdf"):
#                 # if f.filename.endswith(".docx") or f.filename.endswith(".doc"):
#                 #     word = win32com.client.Dispatch("Word.Application")
#                 #     a = word.Documents.Open(f)
#                 #     a.SaveAs(f, FileFormat=17)
#                 # else:
#                 f = img2pdf.convert(f, rotation=img2pdf.Rotation.ifvalid)
#                 merger.append(BytesIO(f))
#             else:
#                 merger.append(BytesIO(f.read()))
#         op = BytesIO()
#         merger.write(op)
#         op.seek(0)
#         pdf_id = PDF.query.count() + 1
#         db.session.add(PDF(id=pdf_id, file=op.read()))
#         db.session.commit()
#         qr_code_url = f'/get_qr_code/{pdf_id}'
#         return render_template("Acknowledgement.html", name=[f.filename for f in files],
#                                qr_code_url=qr_code_url)


@app.route('/uploadFiles', methods=['POST'])
def success():
    if request.method == 'POST':
        files = request.files.getlist('files[]')
        pdf_id = PDF.query.count() + 1
        abc = BytesIO()
        zip_file = ZipFile(abc, 'w')
        for f in files:
            zip_file.writestr(f.filename, f)
            # db.session.add(PDF(id=pdf_id, file=f.read()))
        # abc.seek(0)
        db.session.add(PDF(id=pdf_id, file=abc.read()))
        db.session.commit()
        qr_code_url = f'/get_qr_code/{pdf_id}'
        return render_template("Acknowledgement.html", name="File", qr_code_url=qr_code_url)


@app.route('/get_file/<fid>', methods=['GET'])
def get_files(fid):
    pdf_entry = PDF.query.get(fid)
    with ZipFile(BytesIO(pdf_entry.file), 'r') as f:
        f.extractall("Files")
        f.close()
    return send_file(BytesIO(pdf_entry.file), as_attachment=True, download_name=f'{fid}.zip')

# @app.route('/get_file/<fid>', methods=['GET'])
# def get_files(fid):
#     entry = PDF.query.filter_by(id=str(fid)).all()
#     print(entry)
#     files = [BytesIO(x.file) for x in entry]
#     return files
#     # return send_file(BytesIO(pdf_entry.file), as_attachment=True, download_name=f'{fid}.pdf')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
