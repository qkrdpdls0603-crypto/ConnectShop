from flask import Blueprint, render_template, request, abort, g
from ConnectShop.models import Product, Review
from collections import defaultdict

# 'product'라는 이름의 블루프린트 생성
bp = Blueprint('product', __name__, url_prefix='/product')

@bp.route('/list')
def product_list():
    sel_category = request.args.get('category')
    search_kw = request.args.get('kw', '')  # 🌟 검색어 가져오기

    query = Product.query

    # 1. 검색어가 있는 경우 (이름, 카테고리, 브랜드에서 검색)
    if search_kw:
        search_format = f'%%{search_kw}%%'
        query = query.filter(
            Product.name.ilike(search_format) |
            Product.category.ilike(search_format) |
            Product.brand.ilike(search_format)
        )
        # 검색 시에는 카테고리 필터를 무시하고 전체에서 찾도록 sel_category를 None 처리할 수 있습니다.
        sel_category = f"'{search_kw}' 검색 결과"

    # 2. 검색어는 없고 카테고리만 선택된 경우
    elif sel_category:
        query = query.filter_by(category=sel_category)

    # 최종 결과 조회
    products = query.all()

    # 브랜드별 그룹화 로직 (기존 코드 유지)
    products_by_brand = {}
    for p in products:
        if p.brand not in products_by_brand:
            products_by_brand[p.brand] = []
        products_by_brand[p.brand].append(p)

    return render_template('product/catalog.html',
                           current_category=sel_category,
                           products_by_brand=products_by_brand,
                           search_kw=search_kw)  # 🌟 검색어 전달

# 2. 상세 페이지 함수
@bp.route('/page/<int:product_id>/')
def page(product_id):
    product = Product.query.get_or_404(product_id)

    # 현재 로그인한 유저가 이 상품에 리뷰를 남겼는지 확인
    has_reviewed = False
    if g.user:
        # 상단에서 Review를 임포트했으므로 바로 사용 가능합니다.
        existing_review = Review.query.filter_by(user_id=g.user.id, product_id=product_id).first()
        if existing_review:
            has_reviewed = True

    return render_template('product/product_page.html',
                           product=product,
                           has_reviewed=has_reviewed)