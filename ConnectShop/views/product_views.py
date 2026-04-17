from flask import Blueprint, render_template, request, abort, g
from ConnectShop.models import Product, Coupon
from collections import defaultdict

# 'product'라는 이름의 블루프린트 생성
bp = Blueprint('product', __name__, url_prefix='/product')


# 1. 카탈로그(목록) 페이지 함수 추가
@bp.route('/list')
def product_list():  # list -> product_list로 변경
    sel_category = request.args.get('category', '스마트폰')

    # DB 조회
    products = Product.query.filter_by(category=sel_category).all()

    products_by_brand = {}
    for p in products:
        if p.brand not in products_by_brand:
            products_by_brand[p.brand] = []
        products_by_brand[p.brand].append(p)

    return render_template('product/catalog.html',
                           current_category=sel_category,
                           products_by_brand=products_by_brand)


# 2. 기존 상세 페이지 함수
@bp.route('/page/<int:product_id>/')
def page(product_id):
    product = Product.query.get_or_404(product_id)
    coupons = []
    if g.user:
        # 로그인한 사용자의 '사용 안 함(False)' 쿠폰만 가져오기
        coupons = Coupon.query.filter_by(user_id=g.user.id, is_used=False).all()
    return render_template('product/product_page.html', product=product, reviews=[], coupons=coupons)


@bp.app_context_processor
def inject_menu_data():
    # 1. 메뉴에 노출하고 싶은 제품의 ID를 사용자님이 원하는 순서대로 적으세요.
    # (예: 각 카테고리별 대표 제품 5개의 ID)
    display_setup = {
        '스마트폰': [1, 13, 21, 29, 37],
        '무선이어폰': [2, 45, 61, 69, 77],
        '스마트워치': [5, 92, 100, 108, 116],
        '태블릿': [124, 132, 140, 148, 156],
        '노트북': [4, 164, 179, 187, 195],
        '헤드폰': [3, 210, 218, 226, 234],
        '블루투스 스피커': [242, 250, 258, 266, 274]
    }

    menu_data = {}
    for cat_name, ids in display_setup.items():
        # 지정한 ID에 해당하는 제품들을 가져오되, 사용자님이 적은 ID 순서대로 정렬해서 가져옵니다.
        products = Product.query.filter(Product.id.in_(ids)).all()
        # 정렬 순서 보장을 위해 다시 한번 정렬 (in_ 쿼리는 순서를 보장하지 않음)
        products.sort(key=lambda p: ids.index(p.id))
        menu_data[cat_name] = products

    return dict(menu_data=menu_data)