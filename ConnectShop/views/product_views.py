from flask import Blueprint, render_template, abort
from ConnectShop.models import Product  # Product 모델 임포트 확인하세요!

# 'product'라는 이름의 블루프린트 생성
bp = Blueprint('product', __name__, url_prefix='/product')


@bp.route('/page/<int:product_id>/')
def page(product_id):
    # 1. DB에서 해당 ID의 상품을 가져옵니다.
    # get_or_404는 상품이 없으면 알아서 404 에러 페이지를 띄워줍니다.
    product = Product.query.get_or_404(product_id)

    # 2. 리뷰 데이터도 일단 비어있는 리스트로 넘기거나, 실제 모델이 있다면 조회합니다.
    # reviews = Review.query.filter_by(product_id=product_id).all() # 나중에 리뷰 구현 시 사용

    # 3. 실제 DB 객체인 'product'를 HTML로 전달합니다.
    return render_template('product/product_page.html', product=product, reviews=[])