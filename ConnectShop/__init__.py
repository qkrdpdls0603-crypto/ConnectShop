from flask import Flask
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

    # 우리가 만든 모델(데이터베이스 구조)을 플라스크가 알 수 있게 등록합니다.
    from . import models

    # ----------------------------------------------------
    # [블루프린트 등록 영역]

    from .views import main_views, auth_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(auth_views.bp)

    # 나중에 views 폴더 안에 각 기능별 파일을 완성하면 아래 주석을 풀고 연결할 것입니다.
    # ----------------------------------------------------
    # from .views import auth_views, product_views, order_views
    # app.register_blueprint(auth_views.bp)
    # app.register_blueprint(product_views.bp)
    # app.register_blueprint(order_views.bp)

    return app