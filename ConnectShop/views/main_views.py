from flask import Blueprint, render_template
from ConnectShop.models import FAQ

# 'main'이라는 이름의 블루프린트 생성 (기본 접속 주소 '/')
bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/')
def index():
    return render_template('base.html')

# 준비 중 페이지 라우트 함수
@bp.route('/preparing')
def preparing():
    return render_template('preparing.html')

# 고객 지원 페이지 라우트 함수
@bp.route('/support')
def support():
    # DB에서 모든 FAQ 데이터를 가져옵니다.
    faq_list = FAQ.query.all()
    # 가져온 데이터를 faq_list라는 이름으로 템플릿에 넘겨줍니다.
    return render_template('support.html', faq_list=faq_list)