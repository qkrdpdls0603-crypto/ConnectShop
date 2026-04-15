from flask import Blueprint, render_template

# 'product'라는 이름의 블루프린트 생성
bp = Blueprint('product', __name__, url_prefix='/product')


@bp.route('/page/<int:product_id>/')
def detail(product_id):
    # 1. DB 연결 전이므로, 화면 확인용 '가짜 상자(dict)'를 만듭니다.
    temp_product = {
        'name': 'Connect Tablet Pro 11',
        'price': 799000,
        'description': '압도적인 성능과 선명한 디스플레이를 경험하세요.',
        'image_path': 'images/banner3.jpeg'  # 아까 올리신 이미지 경로
    }

    # 2. 'product'라는 이름으로 이 상자를 HTML에 전달합니다.
    # 이렇게 하면 {{ product.name }} 에러가 사라집니다!
    return render_template('product/product_page.html', product=temp_product, reviews=[])
