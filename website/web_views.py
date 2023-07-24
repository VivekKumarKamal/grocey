
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

        new_prod_id = db.session.query(db.func.max(Product.id)).scalar()
        new_prod_id = 1 if not new_prod_id else new_prod_id + 1

        return render_template("seller_home.html",
                               app_name=app_name,
                               new_category_id=new_category_id,
                               categories=categories,
                               new_product_id=new_prod_id)
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
            new_prod_id = db.session.query(db.func.max(Product.id)).scalar()
            new_prod_id = 1 if not new_prod_id else new_prod_id + 1
            return redirect(f"/seller/{new_cat.id}/product/{new_prod_id}")
        else:
            cat.name = name
            db.session.commit()
            return redirect(url_for('web_views.sell'))
    name = cat.name if cat else ""
    new_prod_id = db.session.query(db.func.max(Product.id)).scalar()
    new_prod_id = 1 if not new_prod_id else new_prod_id + 1

    return render_template('/seller_functions/create_category.html',
                           app_name=app_name,
                           category_name=name,
                           category_id=category_id)



@views.route('/seller/<int:cat_id>/product/<int:pro_id>', methods=['GET', 'POST'])        
@login_required
def product(cat_id, pro_id):
    if not current_user.is_seller:
        flash("You can't access this page", category='error')
        return redirect(url_for('web_views.home', app_name=app_name))
    product = Product.query.filter_by(id=pro_id).first()
    if request.method == 'POST':
        name = request.form.get('name')
        unit = request.form.get('unit')
        price = request.form.get('price')
        quantity = request.form.get('quantity')
        expiry_date = request.form.get('expiry_date')

        if not (name and unit and price and quantity and expiry_date):
            flash("Fill all the details!", category='error')

        if not product:
            new_prod = Product(name=name, id=pro_id, unit=unit, price=price, quantity=quantity, category_id=cat_id, expiry_date=expiry_date)
            db.session.add(new_prod)
            db.session.commit()
        else:
            product.name = name
            product.unit = unit
            product.price = price
            product.quantity = quantity
            product.expiry_date = expiry_date

            db.session.commit()
        return redirect(url_for('web_views.sell'))
    category_name = Category.query.filter_by(id=cat_id).first().name
    return render_template('/seller_functions/create_product.html', app_name=app_name, category_name=category_name, product=product)


@views.route('/delete-category/<int:id>')
@login_required
def delete_category(id):
    if current_user.is_seller:
        cat = Category.query.filter_by(id=id).first()
        if cat:
            for prod in cat.products:
                db.session.delete(prod)
            db.session.delete(cat)
            db.session.commit()
            return redirect(url_for('web_views.sell'))
    flash("You don't have permission to delete", category='error')
    return redirect(url_for('web_views.home'))

@views.route('/delete-product/<int:id>')
@login_required
def delete_product(id):
    if current_user.is_seller:
        prod = Product.query.filter_by(id=id).first()
        if prod:
            db.session.delete(prod)
            db.session.commit()
            return redirect(url_for('web_views.home'))
    flash("You don't have permission to delete", category='error')
    return redirect(url_for('web_views.home'))
