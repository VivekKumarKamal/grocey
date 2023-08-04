from . import db
from flask_login import UserMixin
from sqlalchemy import func, ForeignKey


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(30))
    is_seller = db.Column(db.Boolean, default=False)

    # relationship with category and orders
    categories = db.relationship('Category')
    orders = db.relationship('Order')
    carts = db.relationship('Cart')
    products = db.relationship('Product', backref='seller')


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)

    # relationship with User
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # relationship with Product, Order
    products = db.relationship('Product', passive_deletes=True, backref='category')
    orders = db.relationship('Order')
    cart = db.relationship('Cart')
    

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    unit = db.Column(db.String(30))
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    expiry_date = db.Column(db.String(40), nullable=False)
    listing_time = db.Column(db.DateTime, nullable=False, default=func.now())

    # relationship with Category, Order
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    orders = db.relationship('Order', backref='product')
    carts = db.relationship('Cart', backref='product')


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    ordered_price = db.Column(db.Integer, nullable=False)
    order_time = db.Column(db.DateTime, default=func.now())
    product_name = db.Column(db.String)
#
#     # Relationship with User
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer)
    time = db.Column(db.DateTime, nullable=False, default=func.now())
#
#     # Relationship with User
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
