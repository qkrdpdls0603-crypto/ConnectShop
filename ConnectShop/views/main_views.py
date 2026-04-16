# ConnectShop/views/main_views.py

from flask import Blueprint, render_template, request, flash, redirect, url_for
from ConnectShop.models import FAQ

# 🌟 이메일 발송을 위해 추가된 모듈
from flask_mail import Message
from ConnectShop import mail

# 'main'이라는 이름의 블루프린트 생성 (기본 접속 주소 '/')
bp = Blueprint('main', __name__, url_prefix='/')


@bp.route('/')
def index():
    # 🌟 팀원이 만든 상품 메인 페이지로 연결
    return render_template('product/main_page.html')


# 회사 소개 페이지 라우트 함수
@bp.route('/company')
def company():
    return render_template('company.html')


# 이용약관 페이지
@bp.route('/terms')
def terms():
    return render_template('policy/terms.html')


# 개인정보처리방침 페이지
@bp.route('/privacy')
def privacy():
    return render_template('policy/privacy.html')


# 고객 지원 페이지 라우트 함수
@bp.route('/support')
def support():
    # DB에서 최신순으로 정렬해서 5개를 가져옵니다.
    faq_list = FAQ.query.order_by(FAQ.id.desc()).limit(5).all()
    # 가져온 데이터를 faq_list라는 이름으로 템플릿에 넘겨줍니다.
    return render_template('support.html', faq_list=faq_list)


# FAQ 페이지 라우트 함수
@bp.route('/faq_board')
def faq_board():
    # 1. 검색어(kw)와 현재 페이지 번호(page)를 가져옵니다. (기본페이지는 1페이지)
    kw = request.args.get('kw', type=str, default='')
    page = request.args.get('page', type=int, default=1)

    # 2. 검색어가 있으면 필터링, 없으면 전체 다 가져오기 준비
    if kw:
        search = f"%%{kw}%%"
        faq_query = FAQ.query.filter(
            FAQ.question.ilike(search) | FAQ.answer.ilike(search) | FAQ.category.ilike(search)
        ).order_by(FAQ.id.desc())
    else:
        faq_query = FAQ.query.order_by(FAQ.id.desc())

    # 3. 🌟 핵심! .all() 대신 .paginate()를 써서 10개씩 자릅니다.
    faq_list = faq_query.paginate(page=page, per_page=10, error_out=False)

    return render_template('support/faq_board.html', faq_list=faq_list, kw=kw)


# 준비 중 페이지 라우트 함수
@bp.route('/preparing')
def preparing():
    return render_template('preparing.html')


@bp.route('/as_guide')
def as_guide():
    return render_template('support/as_guide.html')


@bp.route('/inquiry', methods=['GET', 'POST'])
def inquiry():
    # POST 요청: 사용자가 '1:1 문의하기' 버튼을 눌렀을 때
    if request.method == 'POST':
        category = request.form.get('category')
        content = request.form.get('content')
        reply_email = request.form.get('email')

        # 1. 🌟 폼에서 이미지 파일 받아오기
        image_file = request.files.get('image')

        # 2. 🌟 이메일 제목 및 받는 사람 설정 (본인 구글 이메일로 변경 필수!)
        subject = f"[ConnectShop 1:1 문의] {category} 관련 문의입니다."
        msg = Message(subject, recipients=['gangto3333@gmail.com'])

        # 3. 🌟 이메일 본문 내용 세팅
        msg.body = f"""
        고객센터에 새로운 1:1 문의가 접수되었습니다.

        ■ 문의 분야: {category}
        ■ 고객 이메일 (답변받을 곳): {reply_email}

        ■ 문의 내용:
        {content}
        """

        # 4. 🌟 이미지가 첨부되었다면 메일에 파일 묶기(Attach)
        if image_file and image_file.filename != '':
            msg.attach(
                image_file.filename,
                image_file.content_type,
                image_file.read()
            )

        # 5. 🌟 메일 최종 발송
        mail.send(msg)

        # 고객에게 성공 메시지를 띄우고 고객센터 메인으로 돌려보냅니다.
        flash('1:1 문의가 성공적으로 접수되었습니다. 기재해주신 이메일로 빠르게 답변해 드리겠습니다.')
        return redirect(url_for('main.support'))

    # GET 요청: 그냥 1:1 문의 페이지에 처음 들어왔을 때 화면 보여주기
    return render_template('support/inquiry.html')