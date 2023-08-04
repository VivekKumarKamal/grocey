
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, login_required, current_user
from . import db, app_name
from .web_models import User, Category, Product, Order, Cart

views = Blueprint('web_views', __name__)


@views.route('/')
def home():
    if current_user.is_authenticated and current_user.is_seller:
        return redirect(url_for('web_views.sell'))
    users = User.query.filter_by(is_seller=1).all()
    categories = {}
    cats = Category.query.filter_by(seller_id=users[0].id)
    for a in cats:
        categories[a] = Product.query.filter_by(category_id=a.id).order_by(Product.listing_time.desc())
    return render_template("home.html", app_name=app_name, categories=categories)


@views.route('/cart')
def cart():
    items = Cart.query.filter_by(user_id=current_user.id).all()
    total_amount = 0
    for i in items:
        total_amount += i.product.price * i.quantity

    return render_template('cart.html', app_name=app_name, items=items, total_amount=total_amount)


@views.route('/orders')
def orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.order_time.desc())

    return render_template('orders.html', app_name=app_name, orders=orders)


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

        return render_template("/seller_functions/seller_home.html",
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
            new_prod = Product(name=name, id=pro_id, unit=unit, price=price, quantity=quantity, category_id=cat_id, expiry_date=expiry_date, seller_id=current_user.id)
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


@views.route('/delete-category/<int:id>', methods=['POST'])
@login_required
def delete_category(id):
    if current_user.is_seller:
        cat = Category.query.filter_by(id=id).first()
        if cat:
            carts = Cart.query.filter_by(product_id=cat.id).all()
            for cart in carts:
                db.session.delete(cart)
                db.session.commit()
            for prod in cat.products:
                db.session.delete(prod)
            db.session.delete(cat)
            db.session.commit()
            return redirect(url_for('web_views.sell'))
    flash("You don't have permission to delete", category='error')
    return redirect(url_for('web_views.home'))

@views.route('/delete-product/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    if current_user.is_seller:
        prod = Product.query.filter_by(id=id).first()
        if prod:
            carts = Cart.query.filter_by(product_id=prod.id).all()
            for cart in carts:
                db.session.delete(cart)
                db.session.commit()
            db.session.delete(prod)
            db.session.commit()
            return redirect(url_for('web_views.home'))
    flash("You don't have permission to delete", category='error')
    return redirect(url_for('web_views.home'))


# ----------- User orders -------------


@views.route('/add-to-cart/<int:id>')
@login_required
def add_to_cart(id):
    product = Product.query.filter_by(id=id).first()
    quantity_ordering = 1

    if product and product.quantity >= quantity_ordering:
        cart = Cart.query.filter_by(product_id=product.id).first()
        if cart:
            cart.quantity += 1
            db.session.commit()
        else:
            new_item_in_cart = Cart(product_id=product.id, category_id=product.category_id, user_id=current_user.id, quantity=quantity_ordering)
            db.session.add(new_item_in_cart)
            db.session.commit()
        flash('Added to Cart', category='success')
        return redirect(url_for('web_views.home'))
    flash("Product quantity not available", category='error')
    return redirect(url_for('web_views.home'))


@views.route('/remove-cart/<int:id>')
@login_required
def remove_cart(id):
    cart = Cart.query.filter_by(id=id).first()

    if cart:
        db.session.delete(cart)
        db.session.commit()
        flash('Removed from Cart', category='success')
        return redirect(url_for('web_views.cart'))
    flash("Error", category='error')
    return redirect(url_for('web_views.cart'))


@views.route('/order/<int:id>')
@login_required
def order_a_item(id):
    product = Product.query.filter_by(id=id).first()
    ordered_price = product.price
    quantity_ordering = 1

    if product and product.quantity >= quantity_ordering:
        order = Order(product_id=product.id, category_id=product.category_id, user_id=current_user.id, quantity=quantity_ordering, ordered_price=ordered_price, product_name=product.name)
        product.quantity -= quantity_ordering
        db.session.add(order)
        db.session.commit()
        flash('Product ordered successfully!', category='success')
        return redirect(url_for('web_views.home'))
    flash("Product quantity not available", category='error')
    return redirect(url_for('web_views.home'))



@views.route('/order-cart')
@login_required
def order_cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()

    for item in cart_items:
        product = Product.query.filter_by(id=item.product_id).first()

        if product and product.quantity >= item.quantity:
            order = Order(product_id=product.id, category_id=product.category_id, user_id=current_user.id, ordered_price=product.price, quantity=item.quantity, product_name=product.name)
            product.quantity -= item.quantity
            db.session.add(order)
            db.session.delete(item)
            db.session.commit()
        else:
            flash('Product/quantity not available', category='error')
            return redirect(url_for('web_views.home'))
    flash('Products ordered successfully!', category='success')
    return redirect(url_for('web_views.home'))


@views.route('/search', methods=['GET', 'POST'])
def search():
    searched = request.form.get('search')
    if not searched:
        return redirect(url_for('web_views.home'))
    lis = set(Product.query.filter(Product.name.like('%' + searched + '%')))
    lis_by_category = list(Category.query.filter(Category.name.like('%' + searched + '%')))

    for a in lis_by_category:
        for prod in a.products:
            lis.add(prod)

    return render_template('search_results.html', searched=searched, products=lis, app_name=app_name)
