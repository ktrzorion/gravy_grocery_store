# LIBRARIES AND PACKAGES AND MODELS

import os
from flask_restful import Api, Resource
from datetime import datetime, timedelta
from flask import Flask, render_template, url_for, redirect, flash, request, session, jsonify
import plotly.express as px
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user
)
from flask_wtf import FlaskForm
from flask_bcrypt import Bcrypt
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    IntegerField,
    HiddenField,
    SelectField,
    EmailField,
)
from wtforms.validators import InputRequired, Length, ValidationError, NumberRange
from functools import wraps
from models import db, User, Admin, Category, Product, Cart, Orders, Order_Item

# DATABASE

current_dir = os.path.abspath(os.path.dirname(__file__))
database_path = os.path.join(current_dir, 'instance', 'database.sqlite3')

app = Flask(__name__)
api = Api(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + database_path
app.config["SECRET_KEY"] = "##120803@@!ktr*zorion"
db.init_app(app)
bcrypt = Bcrypt()

@app.after_request
def after_request(response):
    db.session.remove()
    return response

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("user_login"))
        return view(*args, **kwargs)

    return wrapped_view

# REGISTRATION FORM

class UserRegisterForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "Username"},
    )
    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(min=8, max=20)],
        render_kw={"placeholder": "Password"},
    )
    f_name = StringField(
        "First_name",
        validators=[InputRequired()],
        render_kw={"placeholder": "First Name"},
    )
    l_name = StringField(
        "Last_name",
        validators=[InputRequired()],
        render_kw={"placeholder": "Last Name"},
    )
    email = EmailField(
        "Email",
        validators=[InputRequired()],
        render_kw={"placeholder": "username@example.com"},
    )
    house_no = StringField(
        "House_Number",
        validators=[InputRequired()],
        render_kw={"placeholder": "T-1234"},
    )
    society = StringField(
        "Society",
        validators=[InputRequired()],
        render_kw={"placeholder": "Sector/Society Name"},
    )
    pincode = IntegerField(
        "Pincode",
        validators=[InputRequired()],
        render_kw={"placeholder": "Enter Postal Code"},
    )
    state = StringField(
        "State", validators=[InputRequired()], render_kw={"placeholder": "State"}
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                "Username already in use!"
            )

class AdminRegisterForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "Username"},
    )
    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(min=8, max=20)],
        render_kw={"placeholder": "Password"},
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                "Username already exists. Please choose a different one."
            )

# LOGIN FORM

class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "Username"},
    )
    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(min=8, max=20)],
        render_kw={"placeholder": "Password"},
    )
    submit = SubmitField("Login")

# CATEGORY FORM

class CategoryForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[InputRequired(), Length(min=3, max=20)],
        render_kw={"placeholder": "Category Name"},
    )
    submit = SubmitField("Edit Products")

    def validate_name(self, name):
        existing_name = Category.query.filter_by(name=name.data).first()
        if existing_name:
            raise ValidationError("Category Already Present")

#  PRODUCT FORM

class ProductForm(FlaskForm):
    name = StringField(
        "Product Name",
        validators=[InputRequired(), Length(min=5, max=20)],
        render_kw={"placeholder": "Product Name"},
    )
    unit = SelectField(
        "Unit",
        choices=[
            ("Rupees / Kilogram", "Rupees / Kilogram"),
            ("Rupees / Litre", "Rupees / Litre"),
            ("Rupees / Dozen", "Rupees / Dozen"),
            ("Rupees / 100 Gram", "Rupees / 100 Gram"),
            ("Rupees / Piece", "Rupees / Piece"),
        ],
        validators=[InputRequired()],
        render_kw={"placeholder": "Unit"},
    )
    rate = IntegerField(
        "Rate",
        validators=[InputRequired(), NumberRange(min=0)],
        render_kw={"placeholder": "Rate"},
    )
    quantity = IntegerField(
        "Quantity",
        validators=[InputRequired(), NumberRange(min=(0))],
        render_kw={"placeholder": "Quantity"},
    )
    category_id = HiddenField("Category ID")
    submit = SubmitField("Save Changes")

# ROUTING

@app.route("/")
def index():
    return render_template("index.html")

# R - HOME PAGE

@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    categories = Category.query.all()
    products = Product.query.all()
    for product in products:
        if product.quantity <= 0:
            product.quantity = "Out Of Stock"
    return render_template("home.html", categories=categories, products=products)

# R - SEARCH

@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.args.get("query")

    product_results = Product.query.filter(Product.name.ilike(f"%{query}%")).all()
    category_results = Category.query.filter(Category.name.ilike(f"%{query}%")).all()

    return render_template("search_result.html", product_results=product_results, category_results=category_results)

@app.route('/user_profile', methods=["GET", "POST"])
@login_required
def user_profile():
    user = User.query.get(current_user.id)

    username = user.username
    full_name = f"{user.f_name} {user.l_name}"
    email = user.email
    address = f"{user.house_no}, {user.society}, {user.pincode}, {user.state}"
    return render_template("user_profile.html", username=username, full_name=full_name, address=address, email=email)

# R - CONTACT

@app.route("/contact")
def contact():
    return render_template("contact.html")

#  R - ABOUT US

@app.route("/about_us")
def about_us():
    return render_template("about_us.html")

# R - DASHBOARD

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    categories = Category.query.all()
    products = Product.query.all()
    return render_template("dashboard.html", categories=categories, products=products)

# R - LOGIN

@app.route("/user_login", methods=["GET", "POST"])
def user_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            session['name'] = user.username
            return redirect(url_for("home"))
    return render_template("user_login.html", form=form)

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and bcrypt.check_password_hash(admin.password, form.password.data):
            login_user(admin)
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password", "danger")
    return render_template("admin_login.html", form=form)

# R - LOGOUT

@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("user_login"))

# R - USER REGISTER

@app.route("/user_register", methods=["GET", "POST"])
def user_register():
    form = UserRegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        if User.query.filter_by(username=username).first():
            error = "Username already exists. Please choose a different username."
            return render_template('user_register.html', form=form, error=error)
        
        else:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
            new_user = User(
                username=form.username.data,
                password=hashed_password,
                f_name=form.f_name.data,
                l_name=form.l_name.data,
                email=form.email.data,
                house_no=form.house_no.data,
                society=form.society.data,
                pincode=form.pincode.data,
                state=form.state.data,
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("user_login"))
    
    return render_template("user_register.html", form=form, error=None)

# R - ADMIN REGISTRATION

@app.route("/admin_register", methods=["GET", "POST"])
def admin_register():
    form = AdminRegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        if Admin.query.filter_by(username=username).first():
            error = "Username already exists. Please choose a different username."
            return render_template('admin_register.html', form=form, error=error)
        
        else:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
            new_admin = Admin(username=form.username.data, password=hashed_password)
            db.session.add(new_admin)
            db.session.commit()
            return redirect(url_for("admin_login"))

    return render_template("admin_register.html", form=form)

# R - ADD CATEGORY

@app.route("/add_category", methods=["GET", "POST"])
@login_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        return redirect(url_for("dashboard"))
    return render_template("add_category.html", form=form)


# R - DELETE CATEGORY

@app.route("/delete-category", methods=["POST"])
def delete_category():
    category_id = request.form.get("id")
    category = Category.query.get(category_id)
    if category:
        Product.query.filter_by(category_id=category_id).delete()
        db.session.delete(category)
        db.session.commit()
    return redirect(url_for("dashboard"))


# R - EDIT CATEGORY

@app.route("/edit_category", methods=["GET", "POST"])
@login_required
def edit_category():
    category_id = request.args.get("id")
    category = Category.query.get(category_id)
    form = CategoryForm(obj=category)

    if request.method == "POST" and form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        return redirect(url_for("dashboard"))

    return render_template(
        "edit_category.html", form=form, category=category, name=category.name
    )

# R - DELETE PRODUCT

@app.route("/delete-product", methods=["POST"])
def delete_product():
    id = request.form.get("id")
    product = Product.query.get(id)
    if product:
        db.session.delete(product)
        db.session.commit()
    return redirect(url_for("dashboard"))

#  R - ADD PRODUCT

@app.route("/add_product", methods=["GET", "POST"])
def add_product():
    form = ProductForm(request.form)
    if form.validate_on_submit():
        print("form validated")
        category_id = int(request.form["category_id"])
        print("Category ID:", category_id)
        new_product = Product(
            name=form.name.data,
            unit=form.unit.data,
            rate=form.rate.data,
            quantity=form.quantity.data,
            category_id=category_id,
        )
        db.session.add(new_product)
        db.session.commit()
        return redirect("/dashboard")
    else:
        print("ERROR")
        print("Form errors:", form.errors)
    return render_template("add_product.html", form=form, name=Product.name)

# R - EDIT PRODUCT

@app.route("/edit_product", methods=["GET", "POST"])
@login_required
def edit_product():
    print("edit_product function accessed")
    product_id = request.args.get("id")
    product = Product.query.get(product_id)
    form = ProductForm(obj=product)

    if request.method == "POST" and form.validate_on_submit():
        product.name = form.name.data
        product.unit = form.unit.data
        product.rate = form.rate.data
        product.quantity = form.quantity.data
        db.session.commit()
        return redirect(url_for("dashboard"))
    else:
        print("ERROR")
        print("Form errors:", form.errors)
    return render_template(
        "edit_product.html", form=form, product_id=product_id, name=product.name
    )

# R - ADD TO CART

@app.route("/add_to_cart", methods=["POST"])
@login_required
def add_to_cart():
    product_id = request.form.get("product_id")
    quantity = int(request.form.get("quantity"))
    product = Product.query.get(product_id)

    if product.quantity <= 0:
        print("Item Out Of Stock!")
        return redirect(url_for("home"))

    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = Cart(
            user_id=current_user.id,
            product_id=product_id,
            product_name=product.name,
            quantity=quantity,
        )
        db.session.add(cart_item)
    
    db.session.commit()

    return redirect(url_for("home"))

# R - REMOVE FROM CART

@app.route("/remove_product/<int:product_id>", methods=["POST"])
def remove_product(product_id):
    product_to_remove = Cart.query.filter_by(product_id=product_id).first()

    if product_to_remove:
        db.session.delete(product_to_remove)
        db.session.commit()
        flash("Product removed from the cart.", "success")
    else:
        flash("Product not found in the cart.", "error")

    return redirect(url_for("cart"))

#  R - DELETE CART

@app.route("/clear_cart", methods=["POST"])
@login_required
def clear_cart():
    if current_user.is_authenticated:
        Cart.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
    else:
        session.pop("cart", None)

    flash("Cart cleared!", "success")
    return redirect(url_for('cart'))

# R - CART

@app.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).join(Product).all()
    item_subtotal = {
        item.cart_id: item.quantity * item.product.rate for item in cart_items
    }
    total_price = sum(item.quantity * item.product.rate for item in cart_items)
    out_of_stock_items = []

    for item in cart_items:
        if item.product.quantity <= 0:
            out_of_stock_items.append(item)
        elif item.quantity > item.product.quantity:
            out_of_stock_items.append(item)

    if out_of_stock_items:
        disable_place_order = True
        flash('Out Of Quantity / Stock Will Be Removed automatically When Refreshed!')
        for item in out_of_stock_items:
            db.session.delete(item)
        db.session.commit()
    else:
        disable_place_order = False

    if request.method == "POST":
        return redirect(url_for("home"))

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total_price=total_price,
        item_subtotal=item_subtotal,
        name=current_user.username,
        disable_place_order=disable_place_order,
    )

# R - ORDER PLACED

@app.route('/ordered', methods=["POST"])
@login_required
def ordered():
    user_id = current_user.id
    user = User.query.get(user_id)

    if user:
        name = f"{user.f_name} {user.l_name}"
        address = f"{user.house_no}, {user.society}, {user.pincode}, {user.state}"

        cart_items = Cart.query.filter_by(user_id=current_user.id).all()
        out_of_stock_items = []

        for item in cart_items:
            if item.product.quantity < item.quantity:
                out_of_stock_items.append(item)
            else:
                item.product.quantity -= item.quantity
                db.session.delete(item)

        if out_of_stock_items:
            db.session.rollback()
            flash("Some items in your cart are out of stock or have insufficient quantity.", "danger")
        else:
            new_order = Orders(name=name, address=address)
            db.session.add(new_order)
            db.session.commit()

            for item in cart_items:
                order_item = Order_Item(
                    order_id=new_order.id, 
                    product_id=item.product_id,
                    category_id=item.product.category_id,
                    product_name=item.product_name,
                    category_name=item.product.category.name,
                    quantity=item.quantity,
                )
                db.session.add(order_item)
            db.session.commit()

        return render_template("order_placed.html")

    else:
        return redirect(url_for("user_login"))

#  API Class - SUMMARY

class SummaryResource(Resource):
    def get(self):
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        last_week_orders = Orders.query.filter(Orders.timestamp >= start_date, Orders.timestamp <= end_date).all()

        product_sales_summary = {}
        category_sales_summary = {}

        for order in last_week_orders:
            for item in order.items:
                product_id = item.product_id
                category_id = item.category_id
                product_name = item.product_name
                quantity = item.quantity

                # Update product sales summary
                if product_id not in product_sales_summary:
                    product_sales_summary[product_id] = {
                        "product_name": product_name,
                        "total_quantity": quantity
                    }
                else:
                    product_sales_summary[product_id]["total_quantity"] += quantity

                # Update category sales summary
                if category_id not in category_sales_summary:
                    category_sales_summary[category_id] = {
                        "category_name": item.category_name,
                        "product_sales": [{"product_name": product_name, "total_quantity": quantity}]
                    }
                else:
                    existing_product = next((p for p in category_sales_summary[category_id]["product_sales"] if p["product_name"] == product_name), None)
                    if existing_product:
                        existing_product["total_quantity"] += quantity
                    else:
                        category_sales_summary[category_id]["product_sales"].append({"product_name": product_name, "total_quantity": quantity})

        product_summary_data = [
            {
                "product_name": data["product_name"],
                "total_quantity": data["total_quantity"]
            }
            for product_id, data in product_sales_summary.items()
        ]

        category_summary_data = [
            {
                "category_name": data["category_name"],
                "product_sales": data["product_sales"]
            }
            for category_id, data in category_sales_summary.items()
        ]

        return jsonify({
            "product_summary": product_summary_data,
            "category_summary": category_summary_data
        })

api.add_resource(SummaryResource, '/api/summary')

# R- SUMMARY

@app.route("/summary")
def summary():
    return render_template("summary.html")

# MAIN

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)