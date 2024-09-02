from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from models import db, Category, Product, User
import os

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Create tables (only necessary if not using migrations)
with app.app_context():
    db.create_all()

# Ensure upload directory exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Serve uploaded files
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Registration Route
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "User already exists"}), 400
    
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], email=data['email'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully"}), 201

# Login Route
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['identifier']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({"message": "Login successful", "user": user.serialize}), 200
    return jsonify({"message": "Invalid credentials"}), 401

# API Routes for Categories and Products
@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([category.serialize for category in categories])

@app.route('/api/categories', methods=['POST'])
def add_category():
    data = request.form
    image = request.files.get('image')
    
    if image:
        filename = f"category_{data['name']}_{image.filename}"
        image.save(os.path.join(UPLOAD_FOLDER, filename))
    else:
        filename = None

    new_category = Category(name=data['name'], image=filename)
    db.session.add(new_category)
    db.session.commit()
    
    return jsonify(new_category.serialize), 201

@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([product.serialize for product in products])

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.serialize)

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.form
    image = request.files.get('image')
    
    if image:
        filename = f"product_{data['name']}_{image.filename}"
        image.save(os.path.join(UPLOAD_FOLDER, filename))
    else:
        filename = None

    new_product = Product(
        name=data['name'],
        price=float(data['price']),
        stock=int(data['stock']),
        description=data.get('description', ''),
        image=filename,
        category_id=int(data['category_id']) if data.get('category_id') else None
    )
    db.session.add(new_product)
    db.session.commit()
    
    return jsonify(new_product.serialize), 201

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'}), 200


@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.form
    image = request.files.get('image')
    
    product.name = data['name']
    product.price = float(data['price'])
    product.stock = int(data['stock'])
    product.description = data.get('description', '')
    product.category_id = int(data['category_id']) if data.get('category_id') else None

    if image:
        filename = f"product_{data['name']}_{image.filename}"
        image.save(os.path.join(UPLOAD_FOLDER, filename))
        product.image = filename

    db.session.commit()
    
    return jsonify(product.serialize), 200


@app.route('/api/dashboard/products-count', methods=['GET'])
def get_products_count():
    count = Product.query.count()
    return jsonify({'count': count})

if __name__ == '__main__':
    app.run(debug=True)
