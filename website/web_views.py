
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, login_required, current_user
from . import db, app_name
from .web_models import User, Category, Product, Order

views = Blueprint('web_views', __name__)


@views.route('/')
def home():
    if current_user.is_authenticated and current_user.is_seller:

        return redirect(url_for('web_views.sell'))
    return render_template("web_base.html", app_name=app_name)


@views.route('/login')
def login():
    return render_template("login_links.html", app_name=app_name)


@views.route('/seller')
@login_required
def sell():
    if current_user.is_seller:
        new_category_id = db.session.query(db.func.max(Category.id)).scalar()
        new_category_id = 1 if not new_category_id else new_category_id + 1
        categories = User.query.filter_by(id=current_user.id).first().categories

        return render_template("seller_home.html", app_name=app_name, new_category_id=new_category_id, categories=categories)
    flash("You are not a seller!", category='error')
    return redirect(url_for("web_views.home"))


@views.route('/seller/category/<int:category_id>', methods=['GET', 'POST'])
@login_required
def category(category_id):
    if not current_user.is_seller:
        flash("You can't access this page", category='error')
        return redirect(url_for('web_views.home', app_name=app_name))

    cat = Category.query.filter_by(id=category_id).first()

    if request.method == 'POST':
        name = request.form.get('category_name')
        if not cat:
            new_cat = Category(name=name, seller_id=current_user.id)
            db.session.add(new_cat)
            db.session.commit()
        else:
            cat.name = name
            db.session.commit()
    
    name = cat.name if cat else ""
    new_prod_id = db.session.query(db.func.max(Product.id)).scalar()
    new_prod_id = 1 if not new_prod_id else new_prod_id + 1

    return render_template('/seller_functions/create_category.html',
                           app_name=app_name,
                           category_name=name,
                           new_prod_id=new_prod_id,
                           category_id=category_id)



@views.route('/seller/<int:cat_id>/product/<int:pro_id>', methods=['GET', 'POST'])        
@login_required
def product(cat_id, pro_id):
    if not current_user.is_seller:
        flash("You can't access this page", category='error')
        return redirect(url_for('web_views.home', app_name=app_name))
    if request.method == 'POST':
        name = request.form.get('name')
        unit = request.form.get('unit')
        price = request.form.get('price')
        quantity = request.form.get('quantity')

        new_prod = Product(name=name, unit=unit, price=price, quantity=quantity, category_id=cat_id)
        db.session.add(new_prod)
        db.session.commit()
        return redirect(url_for('web_views.sell'))
    return render_template('/seller_functions/create_product.html')
