from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    image = db.Column(db.String(255))  # Store image path
    products = db.relationship('Product', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'image': self.image
        }

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(255))  # Store image path
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'stock': self.stock,
            'description': self.description,
            'image': self.image,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)  # Hashed password

    def __repr__(self):
        return f'<User {self.username}>'
    
    @property
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }
