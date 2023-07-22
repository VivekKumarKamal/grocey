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


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)

    # relationship with User
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # relationship with Product, Order
    products = db.relationship('Product')
    orders = db.relationship('Order')
    

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    unit = db.Column(db.String(30))
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    listing_time = db.Column(db.DateTime, nullable=False, default=func.now())

    # relationship with Category, Order
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    orders = db.relationship('Order', backref='product', passive_deletes=True)
#
#
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer)
    order_time = db.Column(db.DateTime, nullable=False, default=func.now())
#
#     # Relationship with User
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)