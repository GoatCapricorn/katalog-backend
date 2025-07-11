import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DATABASE = 'produk.db'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db()
    produk = conn.execute("SELECT * FROM produk").fetchall()
    return render_template('index.html', produk=produk)

@app.route('/api/produk')
def api_produk():
    conn = get_db()
    produk = conn.execute("SELECT * FROM produk").fetchall()
    return jsonify([dict(row) for row in produk])

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
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        gambar_url = f"/static/uploads/{filename}"

        conn.execute("INSERT INTO produk (nama, harga, link, gambar) VALUES (?, ?, ?, ?)",
                     (nama, harga, link, gambar_url))
        conn.commit()
        return redirect('/admin')

    produk = conn.execute("SELECT * FROM produk").fetchall()
    return render_template('admin.html', produk=produk)
import os

def insert_dummy_data():
    import sqlite3
    conn = sqlite3.connect("produk.db")
    cur = conn.cursor()

    # Buat tabel kalau belum ada
    cur.execute('''
        CREATE TABLE IF NOT EXISTS produk (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT,
            harga INTEGER,
            gambar TEXT,
            link TEXT
        )
    ''')

    # Tambahkan data dummy
    dummy_produk = [
        ("Tas Kulit Wanita", 120000, "https://images.tokopedia.net/img/cache/700/VqbcmM/2023/7/20/bca3bd6d-7504-4c88-a501-7aa8a9604c8f.jpg", "https://shopee.co.id/product/12345"),
        ("Sepatu Sneakers Pria", 210000, "https://images.tokopedia.net/img/cache/700/product-1/2023/2/10/34567.jpg", "https://shopee.co.id/product/67890"),
        ("Jam Tangan Digital", 95000, "https://images.tokopedia.net/img/cache/700/product-1/2022/5/9/12345.jpg", "https://shopee.co.id/product/112233")
    ]

    cur.executemany("INSERT INTO produk (nama, harga, gambar, link) VALUES (?, ?, ?, ?)", dummy_produk)
    conn.commit()
    conn.close()
    print("✅ Dummy produk berhasil dimasukkan ke database.")


if __name__ == '__main__':
    insert_dummy_data()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

