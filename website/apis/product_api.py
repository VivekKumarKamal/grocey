from flask_restful import Resource, marshal_with, fields, reqparse
from website.web_models import Product, User, Category
from website.validations import NotFoundError
from website import db
from werkzeug.security import check_password_hash


product_fields = {
    "name": fields.String,
    "unit": fields.String,
    "price": fields.Float,
    "quantity": fields.Integer,
    "expiry_date": fields.String,
    "listing_time": fields.DateTime,
    "category_id": fields.Integer,
    "seller_id": fields.Integer
}
product_parser = reqparse.RequestParser()
product_parser.add_argument("user_name")
product_parser.add_argument("password")
product_parser.add_argument("name")
product_parser.add_argument("unit")
product_parser.add_argument("price")
product_parser.add_argument("quantity")
product_parser.add_argument("expiry_date")
product_parser.add_argument("category_id")


class ProductAPI(Resource):
    @marshal_with(product_fields)
    def get(self, id):
        product = Product.query.filter_by(id=id).first()
        if product:
            return product
        else:
            raise NotFoundError(status_code=404)

    def put(self, id):
        args = product_parser.parse_args()
        user_name = args.get('user_name')
        password = args.get('password')
        name = args.get('name')
        unit = args.get('unit')
        price = args.get('price')
        quantity = args.get('quantity')
        expiry_date = args.get('expiry_date')

        user = User.query.filter_by(user_name=user_name, is_seller=True).first()
        if not(user and check_password_hash(user.password, password)):
            return "Wrong user_name/password", 400
        product = Product.query.filter_by(id=id, seller_id=user.id).first()
        if not product:
            return "Wrong id", 404
        if not (name and unit and price and quantity and expiry_date):
            return "Give all the details", 400
        product.name = name
        product.unit = unit
        product.price = price
        product.quantity = quantity
        product.expiry_date = expiry_date
        db.session.commit()
        return 'Product updated successfully', 200

    def delete(self, id):
        args = product_parser.parse_args()
        user_name = args.get('user_name')
        password = args.get('password')
        user = User.query.filter_by(user_name=user_name, is_seller=True).first()
        if not (user and check_password_hash(user.password, password)):
            return "Wrong password or user_name", 400
        product = Product.query.filter_by(id=id, seller_id=user.id).first()
        if not product:
            return "Wrong id", 404
        db.session.delete(product)
        db.session.commit()
        return "Product deleted successfully", 200

    def post(self):
        args = product_parser.parse_args()
        user_name = args.get('user_name')
        password = args.get('password')
        name = args.get('name')
        unit = args.get('unit')
        price = args.get('price')
        quantity = args.get('quantity')
        expiry_date = args.get('expiry_date')
        category_id = args.get('category_id')

        user = User.query.filter_by(user_name=user_name, is_seller=True).first()
        if not (user and check_password_hash(user.password, password)):
            return "Wrong user_name/password", 400
        category = Category.query.filter_by(id=category_id, seller_id=user.id).first()
        if not category:
            return "Wrong category", 404
        if not (name and unit and price and quantity and expiry_date):
            return "Give all the details", 400
        new_product = Product(name=name, unit=unit, price=price, quantity=quantity, expiry_date=expiry_date, category_id=category_id, seller_id=1)
        db.session.add(new_product)
        db.session.commit()
        return 'Product created successfully', 200

