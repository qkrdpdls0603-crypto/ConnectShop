from flask import Blueprint, render_template
from ConnectShop.models import FAQ  # 팀장님이 추가한 FAQ 모델

# 'main'이라는 이름의 블루프린트 생성
bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/')
def index():
    # 사용자님이 작업하신 상품 메인 페이지를 첫 화면으로 설정합니다.
    return render_template('product/main_page.html')

# 준비 중 페이지 (팀장님 코드)
@bp.route('/preparing')
def preparing():
    return render_template('preparing.html')

# 고객 지원 페이지 (팀장님 코드)
@bp.route('/support')
def support():
    # DB에서 FAQ 데이터를 가져와서 support.html에 뿌려줍니다.
    faq_list = FAQ.query.all()
    return render_template('support.html', faq_list=faq_list)