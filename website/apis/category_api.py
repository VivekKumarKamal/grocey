from flask_restful import Resource, marshal_with, fields, reqparse
from website.web_models import Category, Product, User
from website.validations import NotFoundError
from website import db
from werkzeug.security import check_password_hash
from flask import jsonify

category_parser = reqparse.RequestParser()
category_parser.add_argument("user_name")
category_parser.add_argument("password")
category_parser.add_argument("name")


class CategoryAPI(Resource):
    def get(self, id):
        category = Category.query.filter_by(id=id).first()
        if category:
            category_output = {
                "id": id,
                "name": category.name,
                "seller_id": category.seller_id,
                "products": [{"id": i.id} for i in category.products]
            }
            return jsonify(category_output)
        else:
            raise NotFoundError(status_code=404)

    def put(self, id):
        args = category_parser.parse_args()
        name = args.get('name', None)
        user_name = args.get('user_name', None)
        password = args.get('password', None)
        if name is None or user_name is None or password is None:
            return "", 400
        user = User.query.filter_by(user_name=user_name, is_seller=True).first()
        if not (user and check_password_hash(user.password, password)):
            return "Wrong password or user_name", 400
        category = Category.query.filter_by(id=id, seller_id=user.id).first()
        if not category:
            return "Wrong id", 404
        category = Category.query.filter_by(id=id, seller_id=user.id).first()
        if not category:
            return "Wrong id", 404
        category.name = name
        db.session.commit()
        return {"id": category.id,
                "name": category.name,
                "seller_id": category.seller_id}, 200

    def delete(self, id):
        args = category_parser.parse_args()
        user_name = args.get('user_name', None)
        password = args.get('password', None)
        if user_name is None or password is None:
            return '', 400
        user = User.query.filter_by(user_name=user_name, is_seller=True).first()
        if not (user and check_password_hash(user.password, password)):
            return "Wrong password or user_name", 400
        category = Category.query.filter_by(id=id, seller_id=user.id).first()
        if not category:
            return "Wrong id", 404
        db.session.delete(category)
        db.session.commit()
        return "Category deleted successfully", 200

    def post(self):
        args = category_parser.parse_args()
        name = args.get('name')
        user_name = args.get('user_name')
        password = args.get('password')
        if name is None or user_name is None or password is None:
            return "", 400
        user = User.query.filter_by(user_name=user_name, is_seller=True).first()
        if not (user and check_password_hash(user.password, password)):
            return "Wrong password or user_name", 400
        new_category = Category(name=name, seller_id=1)
        db.session.add(new_category)
        db.session.commit()
        return {"id": new_category.id,
                "name": name,
                "seller_id": new_category.seller_id}, 200