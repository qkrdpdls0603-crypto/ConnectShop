from flask import Blueprint, render_template, request, abort
from ConnectShop.models import Product
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
    return render_template('product/product_page.html', product=product, reviews=[])