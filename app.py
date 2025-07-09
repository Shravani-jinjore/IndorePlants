from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for sessions

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2908",
    database="indoorplants"
)

@app.route("/")
def home():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    return render_template("home.html", products=products)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        cursor.close()
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        if user:
            session['user_id'] = user['id']
            return redirect(url_for('home'))
        else:
            return "Invalid credentials"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('cart', None)
    return redirect(url_for('home'))

@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    cursor.close()

    if not product:
        return "Product not found!", 404

    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append({
        'id': product['id'],
        'name': product['name'],
        'price': product['price'],
        'image_url': product['image_url']
    })
    session.modified = True
    return redirect(url_for('cart'))

@app.route("/cart")
def cart():
    cart_items = session.get('cart', [])
    return render_template("cart.html", cart=cart_items)

@app.route("/remove_from_cart/<int:index>")
def remove_from_cart(index):
    if 'cart' in session:
        cart = session['cart']
        if 0 <= index < len(cart):
            cart.pop(index)
            session['cart'] = cart
    return redirect(url_for('cart'))

if __name__ == "__main__":
    app.run(debug=True)
