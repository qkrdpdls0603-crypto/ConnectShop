from flask import Blueprint, render_template

# 'product'라는 이름의 블루프린트 생성
bp = Blueprint('product', __name__, url_prefix='/product')

@bp.route('/detail/<int:product_id>/')
def detail(product_id):
    # 실제 프로젝트에서는 여기서 DB 조회를 하겠죠?
    # 예: product = Product.query.get_or_404(product_id)
    return render_template('product/product_page.html')