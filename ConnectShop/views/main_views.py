from flask import Blueprint, render_template

# 'main'이라는 이름의 블루프린트 생성 (기본 접속 주소 '/')
bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/')
def index():
    return render_template('base.html')
