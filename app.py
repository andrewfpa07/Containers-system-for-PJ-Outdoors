from flask import Flask, render_template, request, redirect
import sqlite3
import threading
import webbrowser

app = Flask(__name__)
DB_FILE = "inventory.db"

# ------------------------
# Utility: Convert SQLite rows to dicts
# ------------------------
def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

# ------------------------
# Initialize SQLite database
# ------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            container INTEGER NOT NULL,
            side TEXT NOT NULL,
            shelf INTEGER NOT NULL,
            quantity INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ------------------------
# Constants
# ------------------------
CONTAINERS = list(range(1, 9))
SIDES = list("A,B,C,D,E,F,G,H,I,J,K,L,M,N".split(","))

# ------------------------
# HOME (Dashboard)
# ------------------------
@app.route('/')
def home():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = dict_factory
    c = conn.cursor()

    # Count products in each container
    c.execute('SELECT container, COUNT(*) AS count FROM products GROUP BY container ORDER BY container')
    rows = c.fetchall()

    containers = {i: 0 for i in CONTAINERS}
    for row in rows:
        containers[row["container"]] = row["count"]

    # Total products
    c.execute('SELECT COUNT(*) AS total FROM products')
    total_products = c.fetchone()["total"]

    # Low stock (quantity <= 2)
    c.execute('SELECT COUNT(*) AS low FROM products WHERE quantity <= 2')
    low_stock = c.fetchone()["low"]

    # Containers used (with at least 1 product)
    containers_used = sum(1 for count in containers.values() if count > 0)

    conn.close()

    return render_template(
        'home.html',
        containers=containers,
        total_products=total_products,
        low_stock=low_stock,
        containers_used=containers_used
    )

# ------------------------
# Index – All Products
# ------------------------
@app.route('/index')
def index():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute('SELECT * FROM products ORDER BY container, shelf')
    products = c.fetchall()
    conn.close()
    return render_template('index.html', products=products)

# ------------------------
# Low Stock Page
# ------------------------
@app.route('/low-stock')
def low_stock_page():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute('SELECT * FROM products WHERE quantity <= 2 ORDER BY container, shelf')
    products = c.fetchall()
    conn.close()
    return render_template('low_stock.html', products=products)

# ------------------------
# Add Product
# ------------------------
@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        container = int(request.form['container'])
        side = request.form['side'].upper()
        shelf = int(request.form['shelf'])
        quantity = int(request.form.get('quantity') or 0)

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO products (name, container, side, shelf, quantity)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, container, side, shelf, quantity))
        conn.commit()
        conn.close()

        return redirect('/add')

    return render_template('add_product.html', containers=CONTAINERS, sides=SIDES)

# ------------------------
# Update Product
# ------------------------
@app.route('/update/<int:product_id>', methods=['GET', 'POST'])
def update_product(product_id):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = dict_factory
    c = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        container = int(request.form['container'])
        side = request.form['side'].upper()
        shelf = int(request.form['shelf'])
        quantity = int(request.form.get('quantity') or 0)

        c.execute('''
            UPDATE products
            SET name=?, container=?, side=?, shelf=?, quantity=?
            WHERE id=?
        ''', (name, container, side, shelf, quantity, product_id))
        conn.commit()
        conn.close()

        return redirect('/index')

    # GET request
    c.execute('SELECT * FROM products WHERE id=?', (product_id,))
    product = c.fetchone()
    conn.close()

    if not product:
        return "Product not found", 404

    return render_template(
        'update_product.html',
        product=product,
        product_id=product_id,
        containers=CONTAINERS,
        sides=SIDES
    )

# ------------------------
# Delete Product
# ------------------------
@app.route('/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM products WHERE id=?', (product_id,))
    conn.commit()
    conn.close()

    return redirect('/index')

# ------------------------
# Search
# ------------------------
@app.route('/search', methods=['GET', 'POST'])
def search_product():
    results = []

    if request.method == 'POST':
        search_name = request.form['name']

        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = dict_factory
        c = conn.cursor()
        c.execute('SELECT * FROM products WHERE name LIKE ?', (f'%{search_name}%',))
        results = c.fetchall()
        conn.close()

    return render_template('search_product.html', results=results)

# ------------------------
# Container View
# ------------------------
@app.route('/container/<int:container_id>')
def container_page(container_id):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute('SELECT * FROM products WHERE container=? ORDER BY shelf', (container_id,))
    products = c.fetchall()
    conn.close()
    return render_template('container.html', container_id=container_id, products=products)

# ------------------------
# Auto-browser
# ------------------------
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

# ------------------------
# Run App
# ------------------------
if __name__ == "__main__":
    threading.Timer(1, open_browser).start()
    app.run(debug=False)
