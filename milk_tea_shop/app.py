import os
from flask import Flask
from werkzeug.security import generate_password_hash
from config import Config
from models import db, Product, User
from routes import main_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["IMAGE_FOLDER"], exist_ok=True)
    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()
        update_database()
        add_sample_users()
        add_sample_products()

    return app


def update_database():
    with db.engine.connect() as conn:
        columns = conn.exec_driver_sql("PRAGMA table_info(orders)").fetchall()
        column_names = [column[1] for column in columns]

        need_columns = {
            "customer_name": "VARCHAR(120) DEFAULT ''",
            "phone": "VARCHAR(30) DEFAULT ''",
            "address": "VARCHAR(255) DEFAULT ''",
            "note": "TEXT DEFAULT ''",
            "status": "VARCHAR(50) DEFAULT 'Chờ xác nhận'",
        }

        for name, data_type in need_columns.items():
            if name not in column_names:
                conn.exec_driver_sql(f"ALTER TABLE orders ADD COLUMN {name} {data_type}")

        conn.commit()


def add_sample_users():
    users = [
        ("admin", "admin123", "admin"),
        ("khach", "123456", "user"),
    ]

    for username, password, role in users:
        old_user = User.query.filter_by(username=username).first()

        if old_user is None:
            user = User(
                username=username,
                password=generate_password_hash(password),
                role=role
            )
            db.session.add(user)

    db.session.commit()


def add_sample_products():
    products = [
        # MENU TRÀ SỮA
        ["Trà sữa matcha", "Trà sữa", "M/L", "Thạch matcha", 38000, "Vị matcha thơm nhẹ, béo vừa.", "Tra_sua_matcha.png"],
        ["Trà sữa trân châu đường đen", "Trà sữa", "M/L", "Trân châu đường đen", 35000, "Trà sữa béo thơm, trân châu dai mềm.", "Tra_sua_tran_chau_duong_den.png"],
        ["Trà sữa truyền thống", "Trà sữa", "M/L", "Trân châu đen", 30000, "Hương vị truyền thống, dễ uống.", "Tra_sua_truyen_thong.png"],
        ["Trà sữa khoai môn", "Trà sữa", "M/L", "Thạch khoai môn", 36000, "Khoai môn thơm béo, màu tím đẹp.", "Tra_sua_khoai_mon.png"],
        ["Trà sữa thái xanh", "Trà sữa", "M/L", "Trân châu trắng", 32000, "Vị trà thái xanh thơm mát.", "Tra_sua_thai_xanh.png"],
        ["Trà sữa chocolate", "Trà sữa", "M/L", "Pudding trứng", 37000, "Vị chocolate ngọt nhẹ.", "Tra_sua_chocolate.png"],
        ["Trà sữa dâu tây", "Trà hoa quả", "M/L", "Thạch dâu", 36000, "Vị dâu chua ngọt dễ uống.", "Tra_sua_dau_tay.png"],
        ["Trà sữa việt quất", "Trà hoa quả", "M/L", "Thạch trái cây", 39000, "Hương việt quất thơm nhẹ.", "Tra_sua_viet_quat.png"],
        ["Trà sữa bơ", "Sữa tươi", "M/L", "Kem cheese", 40000, "Vị bơ béo mịn.", "Tra_sua_bo.png"],
        ["Hồng trà machiato", "Trà hoa quả", "M/L", "Kem cheese", 35000, "Hồng trà kết hợp kem machiato.", "Hong_tra_machiato.png"],

        # MENU TOPPING
        ["Trân châu đen", "Topping", "Không", "Không", 5000, "Topping trân châu đen dai mềm.", "logo.png"],
        ["Trân châu đường đen", "Topping", "Không", "Không", 8000, "Trân châu nấu với đường đen, vị ngọt thơm.", "logo.png"],
        ["Thạch trái cây", "Topping", "Không", "Không", 6000, "Thạch trái cây nhiều màu, vị ngọt nhẹ.", "logo.png"],
        ["Thạch matcha", "Topping", "Không", "Không", 7000, "Thạch matcha thơm nhẹ, hợp với trà sữa.", "logo.png"],
        ["Thạch phô mai", "Topping", "Không", "Không", 8000, "Thạch phô mai béo nhẹ, ăn kèm trà sữa.", "logo.png"],
        ["Sương sáo", "Topping", "Không", "Không", 6000, "Sương sáo thanh mát, mềm nhẹ.", "logo.png"],
        ["Nha đam", "Topping", "Không", "Không", 6000, "Nha đam giòn mát, phù hợp với trà hoa quả.", "logo.png"],
    ]

    for item in products:
        old_product = Product.query.filter_by(name=item[0]).first()

        if old_product is None:
            product = Product(
                name=item[0],
                category=item[1],
                size=item[2],
                topping=item[3],
                price=item[4],
                description=item[5],
                image=item[6]
            )
            db.session.add(product)

    db.session.commit()


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
