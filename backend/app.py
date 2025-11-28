from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time

app = Flask(__name__)

# === Конфигурация БД ===
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("POSTGRES_HOST")
REQUEST_COUNT = Counter(
    "minishop_requests_total", 
    "Total requests", 
    ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "minishop_request_latency_seconds", 
    "Request latency",
    ["endpoint"]
)
ERROR_COUNT = Counter(
    "minishop_errors_total", 
    "Total errors", 
    ["status_code"]
)
PRODUCT_COUNT = Gauge(
    "minishop_products_total",
    "Total number of products in database"
)
BUSINESS_ORDERS = Counter(
    "minishop_business_orders_total",
    "Total business orders (product additions)",
    ["product_type"]
)

if DB_USER and DB_PASSWORD and DB_NAME and DB_HOST:
    # Если заданы переменные окружения → работаем с Postgres
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
else:
    # Иначе локальная SQLite (для заказчика)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ===== Модель товара =====
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)  # новое поле

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    # Log request details
    latency = time.time() - request.start_time
    REQUEST_LATENCY.labels(endpoint=request.path).observe(latency)
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code
    ).inc()
    
    if response.status_code >= 400:
        ERROR_COUNT.labels(status_code=response.status_code).inc()
    
    return response

# ===== Веб-страницы =====
@app.route('/')
def index():
    products = Product.query.all()
    return render_template("index.html", products=products)

def update_product_count():
    """Update product count metric"""
    count = Product.query.count()
    PRODUCT_COUNT.set(count)

@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    price = float(request.form['price'])
    description = request.form.get('description', '')  # новое поле
    new_product = Product(name=name, price=price, description=description)
    db.session.add(new_product)
    db.session.commit()

    # Business metrics
    BUSINESS_ORDERS.labels(product_type="web_form").inc()
    update_product_count()

    return redirect(url_for('index'))

# ===== API =====
@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([
        {"id": p.id, "name": p.name, "price": p.price, "description": p.description}
        for p in products
    ])

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify({"id": product.id, "name": product.name,
                        "price": product.price, "description": product.description})
    return jsonify({"error": "Product not found"}), 404

@app.route('/add_product', methods=['POST'])
def add_product():
    data = request.get_json()
    new_product = Product(
        name=data['name'],
        price=data['price'],
        description=data.get('description', '')
    )
    db.session.add(new_product)
    db.session.commit()

    BUSINESS_ORDERS.labels(product_type="api").inc()
    update_product_count()

    return jsonify({"message": "Product added"}), 201

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
