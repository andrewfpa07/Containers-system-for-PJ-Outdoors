from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Initialize the database
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

# Route to add a product
@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        container = request.form['container']
        side = request.form['side'].upper()
        shelf = request.form['shelf']
        quantity = request.form.get('quantity', 0)

        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        c.execute('INSERT INTO products (name, container, side, shelf, quantity) VALUES (?, ?, ?, ?, ?)',
                  (name, container, side, shelf, quantity))
        conn.commit()
        conn.close()

        return redirect('/add')

    return render_template('add_product.html')

# Route to search products
@app.route('/search', methods=['GET', 'POST'])
def search_product():
    results = []
    if request.method == 'POST':
        search_name = request.form['name']
        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        c.execute('SELECT name, container, side, shelf, quantity FROM products WHERE name LIKE ?', (f'%{search_name}%',))
        results = c.fetchall()
        conn.close()

    return render_template('search_product.html', results=results)

# Redirect home to add product page
@app.route('/')
def home():
    return redirect('/add')

if __name__ == '__main__':
    app.run(debug=True)

