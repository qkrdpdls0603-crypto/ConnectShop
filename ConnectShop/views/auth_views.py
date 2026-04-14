import functools

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.functions import current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ConnectShop import db
from ConnectShop.forms import UserCreateForm, UserLoginForm, FindIdForm, ResetPasswordForm, UserUpdateForm
from ConnectShop.models import User



bp = Blueprint('auth', __name__, url_prefix='/auth')


# 1. 회원가입
@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = UserCreateForm()
    if request.method == 'POST' and form.validate_on_submit():
        # 중복 검사: 이메일과 이름(username) 기준

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
            password=generate_password_hash(form.password1.data)
        )

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('이미 가입된 정보가 있습니다.')
            return render_template('auth/signup.html', form=form)

        flash('회원가입이 완료되었습니다. 로그인 해주세요.')
        return redirect(url_for('auth.login'))

    return render_template('auth/signup.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    form = UserLoginForm()

    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if not user:
            error = "등록되지 않은 이메일입니다."
        elif not check_password_hash(user.password, form.password.data):
            error = "비밀번호가 맞지 않습니다."
        else:

            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('main.index'))

        flash(error)

    return render_template('auth/login.html', form=form)



# 3. 로그아웃
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))


# 4. 아이디(이메일) 찾기
@bp.route('/find_id', methods=['GET', 'POST'])
def find_id():
    # 파인드인포html에서 사용하는 두 가지 폼을 모두 전달
    find_id_form = FindIdForm()
    reset_pw_form = ResetPasswordForm()

    if request.method == 'POST' and find_id_form.validate_on_submit():
        user = User.query.filter_by(
            username=find_id_form.username.data,
            mobile=find_id_form.phone.data  # 핸드폰 번호 조건 추가
        ).first()
        if user:
            flash(f"찾으시는 이메일은 {user.email} 입니다.")
        else:
            flash("가입된 정보가 없습니다.")

    return render_template('auth/find_info.html',
                           find_id_form=find_id_form,
                           reset_pw_form=reset_pw_form)


# 5. 비밀번호 재설정
@bp.route('/find_password', methods=['GET', 'POST'])
def find_password():
    find_id_form = FindIdForm()
    reset_pw_form = ResetPasswordForm()

    if request.method == 'POST' and reset_pw_form.validate_on_submit():
        # 이름과 이메일이 동시에 일치하는지 확인 [cite: 1, 10]
        user = User.query.filter_by(username=reset_pw_form.username.data,
                                    email=reset_pw_form.email.data).first()
        if user:
            user.password = generate_password_hash(reset_pw_form.password1.data)
            db.session.commit()
            flash("비밀번호가 성공적으로 변경되었습니다.")
            return redirect(url_for('auth.login'))
        else:
            flash("입력하신 정보와 일치하는 사용자가 없습니다.")

    return render_template('auth/find_info.html',
                           find_id_form=find_id_form,
                           reset_pw_form=reset_pw_form)


# 라우팅 함수보다 먼저 실행하는 함수
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)


# 데코레이션 함수 (멤버십처럼 진행도?)
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            _next = request.url if request.method == 'GET' else ''
            return redirect(url_for('auth.login', next=_next))
        return view(*args, **kwargs)

    return wrapped_view


@bp.route('/mypage')
@login_required
def mypage():
    user = User.query.get(session['user_id'])
    return render_template('auth/mypage.html', user=user)


@bp.route('/orders')
@login_required
def cart_list():
    return render_template('order/cart_list.html')


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
