from flask import Flask
from werkzeug.security import generate_password_hash

from config import Config
from models import db, Product, User
from routes import main_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()
        add_sample_users()
        add_sample_products()

    return app


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
        ["Trà sữa matcha", "Trà sữa", "M/L", "Thạch matcha", 38000, "Vị matcha thơm nhẹ, béo vừa.", "Tra_sua_matcha.png"],
        ["Trà sữa trân châu đường đen", "Trà sữa", "M/L", "Trân châu đường đen", 35000, "Trà sữa béo thơm, trân châu dai mềm.", "Tra_sua_tran_chau_duong_den.png"],
        ["Trà sữa truyền thống", "Trà sữa", "M/L", "Trân châu đen", 30000, "Hương vị truyền thống, dễ uống.", "Tra_sua_truyen_thong.png"],
        ["Trà sữa khoai môn", "Trà sữa", "M/L", "Thạch khoai môn", 36000, "Khoai môn thơm béo, màu tím đẹp.", "Tra_sua_khoai_mon.png"],
        ["Trà sữa thái xanh", "Trà sữa", "M/L", "Trân châu trắng", 32000, "Vị trà thái xanh thơm mát.", "Tra_sua_thai_xanh.png"],
        ["Trà sữa chocolate", "Trà sữa", "M/L", "Pudding trứng", 37000, "Vị chocolate ngọt nhẹ.", "Tra_sua_chocolate.png"],
        ["Trà sữa dâu tây", "Trà sữa", "M/L", "Thạch dâu", 36000, "Vị dâu chua ngọt dễ uống.", "Tra_sua_dau_tay.png"],
        ["Trà sữa việt quất", "Trà sữa", "M/L", "Thạch trái cây", 39000, "Hương việt quất thơm nhẹ.", "Tra_sua_viet_quat.png"],
        ["Trà sữa bơ", "Trà sữa", "M/L", "Kem cheese", 40000, "Vị bơ béo mịn.", "Tra_sua_bo.png"],
        ["Hồng trà machiato", "Trà sữa", "M/L", "Kem cheese", 35000, "Hồng trà kết hợp kem machiato.", "Hong_tra_machiato.png"],

        ["Trân châu đen", "Topping", "Không", "Không", 5000, "Topping trân châu đen dai mềm.", "topping_tran_chau_duong_den.png"],
        ["Trân châu đường đen", "Topping", "Không", "Không", 8000, "Trân châu nấu với đường đen, vị ngọt thơm.", "topping_tran_chau_duong_den.png"],
        ["Thạch trái cây", "Topping", "Không", "Không", 6000, "Thạch trái cây nhiều màu, vị ngọt nhẹ.", "topping_thach_trai_cay.png"],
        ["Thạch matcha", "Topping", "Không", "Không", 7000, "Thạch matcha thơm nhẹ, hợp với trà sữa.", "topping_thach_matcha.png"],
        ["Thạch phô mai", "Topping", "Không", "Không", 8000, "Thạch phô mai béo nhẹ, ăn kèm trà sữa.", "topping_thach_pho_mai.png"],
        ["Sương sáo", "Topping", "Không", "Không", 6000, "Sương sáo thanh mát, mềm nhẹ.", "topping_suong_sao.png"],
        ["Nha đam", "Topping", "Không", "Không", 6000, "Nha đam giòn mát, phù hợp với trà sữa.", "topping_nha_dam.png"],
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