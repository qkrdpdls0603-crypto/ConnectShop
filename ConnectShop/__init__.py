from flask import Flask, g, session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import config

# 전역 변수로 db, migrate 객체를 생성합니다.
db = SQLAlchemy()
migrate = Migrate()


def create_app():
    # 플라스크 앱 인스턴스 생성
    app = Flask(__name__)

    # config.py 파일에 작성한 항목들을 앱의 환경 변수로 부릅니다.
    app.config.from_object(config)

    # ORM (데이터베이스) 연동
    db.init_app(app)
    migrate.init_app(app, db)

    # 요약 장바구니 데이터 주입 로직
    @app.context_processor
    def inject_cart():
        from .models import Product, Cart
        from flask import g, session

        cart_items = []
        total_price = 0

        try:
            if hasattr(g, 'user') and g.user:
                db_items = Cart.query.filter_by(user_id=g.user.id).all()
                for item in db_items:
                    if item.product:
                        cart_items.append({
                            'product_id': item.product.id,
                            'product_name': item.product.name,
                            'quantity': item.quantity,
                            'price': item.product.price,
                            'image': item.product.image_path
                        })
                        total_price += item.product.price * item.quantity
            else:
                guest_cart = session.get('guest_cart', [])
                for item in guest_cart:
                    product = Product.query.get(item.get('product_id'))
                    if product:
                        cart_items.append({
                            'product_id': product.id,
                            'product_name': product.name,
                            'quantity': item['quantity'],
                            'price': product.price,
                            'image': product.image_path
                        })
                        total_price += product.price * item['quantity']
        except Exception as e:
            print(f"Cart Injection Error: {e}")

        return dict(cart_items=cart_items, total_price=total_price)

    # 우리가 만든 모델(데이터베이스 구조)을 플라스크가 알 수 있게 등록합니다.
    from . import models

    # ----------------------------------------------------
    # [블루프린트 등록 영역]

    from .views import main_views, auth_views, order_views, product_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(auth_views.bp)
    app.register_blueprint(order_views.bp, url_prefix='/order')
    app.register_blueprint(product_views.bp)
    # 나중에 views 폴더 안에 각 기능별 파일을 완성하면 아래 주석을 풀고 연결할 것입니다.
    # ----------------------------------------------------
    # from .views import auth_views, product_views, order_views
    # app.register_blueprint(auth_views.bp)
    # app.register_blueprint(order_views.bp)

    return app