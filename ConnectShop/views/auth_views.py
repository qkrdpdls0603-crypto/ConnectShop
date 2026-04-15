import functools
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from ConnectShop import db
from ConnectShop.forms import UserCreateForm, UserLoginForm, FindIdForm, ResetPasswordForm
from ConnectShop.models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')


# 1. 회원가입
@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = UserCreateForm()
    if request.method == 'POST' and form.validate_on_submit():
        # 중복 검사
        if User.query.filter_by(email=form.email.data).first():
            flash('이미 등록된 이메일입니다.')
            return render_template('auth/signup.html', form=form)

        if User.query.filter_by(username=form.username.data).first():
            flash('이미 존재하는 이름입니다.')
            return render_template('auth/signup.html', form=form)

        if User.query.filter_by(phone=form.phone.data).first():
            flash('이미 존재하는 전화번호입니다.')
            return render_template('auth/signup.html', form=form)

        user = User(
            email=form.email.data,
            username=form.username.data,
            phone=form.phone.data,
            password=generate_password_hash(form.password1.data),  # <-- 콤마 추가됨
            is_membership=False
        )

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('이미 가입된 정보가 있습니다.')
            return render_template('auth/signup.html', form=form)

        flash('회원가입이 완료되었습니다. 로그인을 진행해 주세요.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/signup.html', form=form)


# 2. 로그인
@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = UserLoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash("등록되지 않은 이메일입니다.", 'danger')
        elif not check_password_hash(user.password, form.password.data):
            flash("비밀번호가 맞지 않습니다.", 'danger')
        else:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('main.index'))

    return render_template('auth/login.html', form=form)


# 3. 로그아웃
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))


# 4. 아이디(이메일) 찾기
@bp.route('/find_id', methods=['GET', 'POST'])
def find_id():
    find_id_form = FindIdForm()
    reset_pw_form = ResetPasswordForm()
    if request.method == 'POST' and find_id_form.validate_on_submit():
        user = User.query.filter_by(
            username=find_id_form.username.data,
            phone=find_id_form.phone.data
        ).first()
        if user:
            flash(f"찾으시는 이메일은 {user.email} 입니다.")
        else:
            flash("가입된 정보가 없습니다.")
    return render_template('auth/find_info.html', find_id_form=find_id_form, reset_pw_form=reset_pw_form)


# 5. 비밀번호 재설정
@bp.route('/find_password', methods=['GET', 'POST'])
def find_password():
    find_id_form = FindIdForm()
    reset_pw_form = ResetPasswordForm()
    if request.method == 'POST' and reset_pw_form.validate_on_submit():
        user = User.query.filter_by(username=reset_pw_form.username.data,
                                    email=reset_pw_form.email.data).first()
        if user:
            user.password = generate_password_hash(reset_pw_form.password1.data)
            db.session.commit()
            flash("비밀번호가 성공적으로 변경되었습니다.")
            return redirect(url_for('auth.login'))
        else:
            flash("입력하신 정보와 일치하는 사용자가 없습니다.")
    return render_template('auth/find_info.html', find_id_form=find_id_form, reset_pw_form=reset_pw_form)


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        # User.query.get(user_id)는 2.0+ 버전에서 지양되므로 필요 시 수정 가능
        g.user = User.query.get(user_id)


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login', next=request.url))
        return view(*args, **kwargs)

    return wrapped_view


@bp.route('/mypage')
@login_required
def mypage():
    # user=user를 user=g.user로 수정
    return render_template('auth/mypage.html', user=g.user)


@bp.route('/orders')
@login_required
def cart_list():
    return render_template('order/cart_list.html')


@bp.route('/withdraw', methods=['POST'])
@login_required
def withdraw():
    # g.user가 존재할 때만 삭제 로직 실행
    if g.user:
        # 일대일 관계인 benefit 먼저 삭제
        if hasattr(g.user, 'benefit') and g.user.benefit:
            db.session.delete(g.user.benefit)

        db.session.delete(g.user)
        db.session.commit()
        session.clear()
        flash("회원 탈퇴가 완료되었습니다.")
    return redirect(url_for('main.index'))



@bp.route('/coupons', endpoint='coupons', methods=['GET'])
@login_required
def coupons_page():
    # 1. 쿠폰 데이터 안전하게 가져오기
    raw_coupons = getattr(g.user, "coupons", []) or []

    # 2. 파이썬에서 미리 분류 (템플릿 부하 감소)
    available_coupons = []
    used_coupons = []

    for c in raw_coupons:
        if getattr(c, "is_used", False):
            used_coupons.append(c)
        else:
            available_coupons.append(c)

    # 3. 정리된 데이터만 템플릿으로 전달
    return render_template(
        'auth/coupons.html',
        available_coupons=available_coupons,
        used_coupons=used_coupons
    )

#구글 로그인
#
# @app.route('/auth/google')
# def google_login():
#     redirect_uri = url_for('google_callback', _external=True)
#     return oauth.google.authorize_redirect(redirect_uri)
#
#
# @app.route('/auth/google/callback')
# def google_callback():
#     token = oauth.google.authorize_access_token()
#     user = token['userinfo']
#
#     email = user['email']
#     name = user['name']
#
#     # 👉 여기서 DB 조회 / 회원 생성 / 로그인 처리
#     return redirect(url_for('main.index'))
