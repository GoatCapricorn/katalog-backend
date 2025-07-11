from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret-key-admin'
CORS(app)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# === Login Manager ===
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# === Koneksi DB ===
def get_db():
    conn = sqlite3.connect('produk.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS produk (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT,
            harga INTEGER,
            gambar TEXT,
            link TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin123':
            user = User(id='admin')
            login_user(user)
            return redirect(url_for('admin'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    conn = get_db()
    if request.method == 'POST':
        nama = request.form['nama']
        harga = request.form['harga']
        link = request.form['link']
        file = request.files['gambar']
        if file.filename != '':
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            gambar_url = f"/static/uploads/{filename}"

            conn.execute("INSERT INTO produk (nama, harga, gambar, link) VALUES (?, ?, ?, ?)",
                         (nama, harga, gambar_url, link))
            conn.commit()
        return redirect(url_for('admin'))

    produk = conn.execute("SELECT * FROM produk").fetchall()
    return render_template('admin.html', produk=produk)

@app.route('/api/produk', methods=['GET'])
def get_produk():
    conn = get_db()
    rows = conn.execute("SELECT nama, harga, gambar, link FROM produk").fetchall()
    produk = [dict(row) for row in rows]
    return jsonify(produk)

@app.route('/api/produk', methods=['POST'])
def tambah_produk_api():
    data = request.get_json()
    if not all(k in data for k in ("nama", "harga", "gambar", "link")):
        return jsonify({"error": "Data tidak lengkap"}), 400

    conn = get_db()
    conn.execute("INSERT INTO produk (nama, harga, gambar, link) VALUES (?, ?, ?, ?)",
                 (data["nama"], data["harga"], data["gambar"], data["link"]))
    conn.commit()
    return jsonify({"message": "Produk ditambahkan"}), 201

if __name__ == '__main__':
    create_table()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
