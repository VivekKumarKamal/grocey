from flask import Flask
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = 'grocery_db.sqlite3'

app_name = "Grocey"

def create_app():
    app = Flask(__name__)
    app.debug = True
    app.config['SECRET_KEY'] = "It's created by Vivek"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    api = Api(app)

    # connecting blueprints/Models with the app
    from .web_models import User
    from .web_models import Category
    from .web_models import Product
    from .web_models import Order
    from .web_models import Cart

    from .web_controllers import views
    from .web_auth import auth

    # without this login won't be possible
    login_manager = LoginManager()
    login_manager.login_view = 'web_views.login'
    login_manager.login_message = 'Please log-in to order products'
    login_manager.init_app(app)

    # Adding Restful Controllers
    from website.apis.category_api import CategoryAPI
    from website.apis.product_api import ProductAPI
    api.add_resource(CategoryAPI, '/api/category', '/api/category/<int:id>')

    api.add_resource(ProductAPI, '/api/product', '/api/product/<int:id>')



    @login_manager.user_loader
    def load_user(id):
        return User.query.get_by_id(int(id))



    app.register_blueprint(views)
    app.register_blueprint(auth)

    with app.app_context():
        db.create_all()

    return app, api