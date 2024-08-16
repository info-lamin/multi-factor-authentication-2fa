import pyotp
import base64
import qrcode
import hashlib
from io import BytesIO
from flask import Flask, render_template, request

app = Flask(__name__)

APP_NAME = 'App Name'
SECRET = 'abcdefghijklmnopqrstuvwxyz'


def encrypt_user_key(user_id):
    combined_text = user_id + SECRET
    encoded_hash = hashlib.md5(combined_text.encode()).hexdigest().encode()
    base32_key = base64.b32encode(encoded_hash).decode()
    return base32_key


def generateQRCode(text: str):
    img = qrcode.make(text)
    buffer = BytesIO()
    img.save(buffer)
    qrCode = f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"
    return qrCode


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/2fa', methods=['GET', 'POST'])
def two_factor():
    username = request.args.get('username')
    submit = request.args.get('submit')

    if submit == 'generate':
        user_key = encrypt_user_key(username)
        totp = pyotp.TOTP(user_key)
        qr_code = generateQRCode(totp.provisioning_uri(
            name=username, issuer_name=APP_NAME))
        return render_template('qrcode.html', qr_code=qr_code)

    if submit == 'validate':
        if request.method == 'GET':
            return render_template('validate.html', username=username)
        if request.method == 'POST':
            user_key = encrypt_user_key(username)
            totp = pyotp.TOTP(user_key)
            input_code = request.form.get('code')
            if totp.verify(input_code):
                return render_template('validate.html', username=username, message='Access granted')
            else:
                return render_template('validate.html', username=username, message='Access denied')


if __name__ == '__main__':
    app.run(debug=True)
