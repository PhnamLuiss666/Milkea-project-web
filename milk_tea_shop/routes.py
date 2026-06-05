from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, User, Product, Order, OrderItem

main_bp = Blueprint("main", __name__)

MAX_QUANTITY = 99
CATEGORIES = ["Tất cả", "Trà sữa", "Topping"]


# =========================
# HÀM DÙNG CHUNG
# =========================
def money(number):
    return f"{number:,.0f}đ".replace(",", ".")


@main_bp.app_context_processor
def send_data_to_html():
    cart = session.get("cart", {})
    cart_count = 0

    for quantity in cart.values():
        try:
            cart_count += int(quantity)
        except:
            pass

    return {
        "money": money,
        "cart_count": cart_count
    }


def check_user():
    if "user_id" not in session:
        flash("Vui lòng đăng nhập trước.", "warning")
        return False

    if session.get("role") == "admin":
        flash("Admin chỉ dùng trang quản lý.", "warning")
        return False

    return True


def check_admin():
    if "user_id" not in session:
        flash("Vui lòng đăng nhập trước.", "warning")
        return False

    if session.get("role") != "admin":
        flash("Bạn không có quyền truy cập trang quản lý.", "danger")
        return False

    return True


# =========================
# ĐĂNG NHẬP / ĐĂNG KÝ
# =========================
@main_bp.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    if session.get("role") == "admin":
        return redirect(url_for("main.dashboard"))

    return redirect(url_for("main.menu"))


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        if session.get("role") == "admin":
            return redirect(url_for("main.dashboard"))
        return redirect(url_for("main.menu"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session.clear()
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role

            flash("Đăng nhập thành công.", "success")

            if user.role == "admin":
                return redirect(url_for("main.dashboard"))

            return redirect(url_for("main.menu"))

        flash("Sai tài khoản hoặc mật khẩu.", "danger")

    return render_template("login.html")


@main_bp.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if username == "" or password == "" or confirm_password == "":
            flash("Vui lòng nhập đầy đủ thông tin.", "danger")
            return redirect(url_for("main.register"))

        if password != confirm_password:
            flash("Mật khẩu nhập lại không khớp.", "danger")
            return redirect(url_for("main.register"))

        old_user = User.query.filter_by(username=username).first()

        if old_user:
            flash("Tên đăng nhập đã tồn tại.", "danger")
            return redirect(url_for("main.register"))

        new_user = User(
            username=username,
            password=generate_password_hash(password),
            role="user"
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Đăng ký thành công. Bạn có thể đăng nhập.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html")


@main_bp.route("/logout")
def logout():
    session.clear()
    flash("Bạn đã đăng xuất.", "info")
    return redirect(url_for("main.login"))


# =========================
# KHÁCH HÀNG
# =========================
@main_bp.route("/menu")
def menu():
    if not check_user():
        return redirect(url_for("main.login"))

    keyword = request.args.get("keyword", "").strip()
    category = request.args.get("category", "Tất cả")

    query = Product.query

    if keyword != "":
        query = query.filter(Product.name.ilike(f"%{keyword}%"))

    if category != "Tất cả":
        query = query.filter(Product.category == category)

    products = query.order_by(Product.id.desc()).all()

    if category == "Tất cả":
        products.sort(key=lambda product: product.category == "Topping")

    return render_template(
        "menu.html",
        products=products,
        categories=CATEGORIES,
        keyword=keyword,
        selected_category=category
    )


@main_bp.route("/cart")
def cart():
    if not check_user():
        return redirect(url_for("main.login"))

    cart = session.get("cart", {})
    cart_items = []
    total_price = 0

    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))

        if product:
            quantity = int(quantity)
            item_total = product.price * quantity
            total_price += item_total

            cart_items.append({
                "product": product,
                "quantity": quantity,
                "item_total": item_total
            })

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total_price=total_price
    )


@main_bp.route("/cart/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    if not check_user():
        return redirect(url_for("main.login"))

    product = Product.query.get_or_404(product_id)

    cart = session.get("cart", {})
    key = str(product.id)

    quantity = request.form.get("quantity", 1, type=int)

    if quantity < 1:
        quantity = 1

    old_quantity = int(cart.get(key, 0))
    new_quantity = old_quantity + quantity

    if new_quantity > MAX_QUANTITY:
        new_quantity = MAX_QUANTITY
        flash("Mỗi món tối đa 99 ly.", "warning")
    else:
        flash("Đã thêm món vào giỏ hàng.", "success")

    cart[key] = new_quantity
    session["cart"] = cart
    session.modified = True

    return redirect(url_for("main.menu"))


@main_bp.route("/cart/update/<int:product_id>", methods=["POST"])
def update_cart(product_id):
    if not check_user():
        return redirect(url_for("main.login"))

    cart = session.get("cart", {})
    key = str(product_id)

    quantity = request.form.get("quantity", 1, type=int)

    if quantity < 1:
        quantity = 1

    if quantity > MAX_QUANTITY:
        quantity = MAX_QUANTITY

    if key in cart:
        cart[key] = quantity
        session["cart"] = cart
        session.modified = True
        flash("Đã cập nhật giỏ hàng.", "success")

    return redirect(url_for("main.cart"))


@main_bp.route("/cart/remove/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    if not check_user():
        return redirect(url_for("main.login"))

    cart = session.get("cart", {})
    cart.pop(str(product_id), None)

    session["cart"] = cart
    session.modified = True

    flash("Đã xóa món khỏi giỏ hàng.", "success")
    return redirect(url_for("main.cart"))


@main_bp.route("/cart/checkout", methods=["POST"])
def checkout_cart():
    if not check_user():
        return redirect(url_for("main.login"))

    cart = session.get("cart", {})

    if not cart:
        flash("Giỏ hàng đang trống.", "warning")
        return redirect(url_for("main.cart"))

    note = request.form.get("note", "").strip()

    total_price = 0
    cart_items = []

    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))

        if product:
            quantity = int(quantity)
            total_price += product.price * quantity

            cart_items.append({
                "product": product,
                "quantity": quantity
            })

    new_order = Order(
        user_id=session.get("user_id"),
        customer_name=session.get("username"),
        phone="",
        address="",
        note=note,
        total_price=total_price,
        status="Chờ xác nhận"
    )

    db.session.add(new_order)
    db.session.flush()

    for item in cart_items:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item["product"].id,
            quantity=item["quantity"],
            price=item["product"].price
        )

        db.session.add(order_item)

    db.session.commit()

    session["cart"] = {}
    session.modified = True

    flash("Đặt hàng thành công! Tổng tiền: " + money(total_price), "success")
    return redirect(url_for("main.my_orders"))


@main_bp.route("/my-orders")
def my_orders():
    if not check_user():
        return redirect(url_for("main.login"))

    orders = Order.query.filter_by(
        user_id=session.get("user_id")
    ).order_by(Order.created_at.desc()).all()

    return render_template("my_orders.html", orders=orders)


# =========================
# ADMIN
# =========================
@main_bp.route("/admin/dashboard")
def dashboard():
    if not check_admin():
        return redirect(url_for("main.login"))

    product_count = Product.query.count()
    order_count = Order.query.count()
    revenue = db.session.query(db.func.sum(Order.total_price)).scalar() or 0

    return render_template(
        "dashboard.html",
        product_count=product_count,
        order_count=order_count,
        revenue=revenue
    )


@main_bp.route("/admin/products")
def admin_products():
    if not check_admin():
        return redirect(url_for("main.login"))

    products = Product.query.order_by(Product.id.desc()).all()

    return render_template("admin_products.html", products=products)


@main_bp.route("/admin/orders")
def order_list():
    if not check_admin():
        return redirect(url_for("main.login"))

    orders = Order.query.order_by(Order.created_at.desc()).all()

    return render_template("order_list.html", orders=orders)