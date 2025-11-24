from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# ------------------------
# Initialize database
# ------------------------
def init_db():
    conn = sqlite3.connect('inventory.db')
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
# HOME PAGE
# ------------------------
@app.route('/')
def home():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('SELECT container, COUNT(*) FROM products GROUP BY container ORDER BY container')
    rows = c.fetchall()
    containers = {row[0]: row[1] for row in rows}

    # Always show containers 3,5,6,7,8
    for cnum in [3,5,6,7,8]:
        if cnum not in containers:
            containers[cnum] = 0

    conn.close()
    return render_template('home.html', containers=containers)

# ------------------------
# INDEX PAGE - ALL PRODUCTS
# ------------------------
@app.route('/index')
def index():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('SELECT name, container, side, shelf, quantity FROM products ORDER BY container, shelf')
    products = c.fetchall()
    conn.close()
    return render_template('index.html', products=products)

# ------------------------
# ADD PRODUCT
# ------------------------
@app.route('/add', methods=['GET','POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        container = request.form['container']
        side = request.form['side'].upper()
        shelf = request.form['shelf']
        quantity = request.form.get('quantity',0)

        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        c.execute('INSERT INTO products (name, container, side, shelf, quantity) VALUES (?, ?, ?, ?, ?)',
                  (name, container, side, shelf, quantity))
        conn.commit()
        conn.close()
        return redirect('/add')
    return render_template('add_product.html')

# ------------------------
# SEARCH PRODUCT
# ------------------------
@app.route('/search', methods=['GET','POST'])
def search_product():
    results = []
    if request.method=='POST':
        search_name = request.form['name']
        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        c.execute('SELECT name, container, side, shelf, quantity FROM products WHERE name LIKE ?', (f'%{search_name}%',))
        results = c.fetchall()
        conn.close()
    return render_template('search_product.html', results=results)

# ------------------------
# CONTAINER PAGE
# ------------------------
@app.route('/container/<int:container_id>')
def container_page(container_id):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('SELECT name, side, shelf, quantity FROM products WHERE container = ? ORDER BY shelf', (container_id,))
    products = c.fetchall()
    conn.close()
    return render_template('container.html', container_id=container_id, products=products)

if __name__ == '__main__':
    app.run(debug=True)
