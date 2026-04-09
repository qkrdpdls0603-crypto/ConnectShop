from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash
# from authlib.integrations.flask_client import OAuth

from ConnectShop import db
from ConnectShop.forms import UserCreateForm, UserLoginForm, FindIdForm, ResetPasswordForm
from ConnectShop.models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = UserCreateForm()
    if request.method == 'POST' and form.validate_on_submit():
        user_email = User.query.filter_by(email=form.email.data).first()
        user_name = User.query.filter_by(username=form.username.data).first()

        if not user_email and not user_name:
            user = User(
                email=form.email.data,
                password=generate_password_hash(form.password1.data),
                username=form.username.data,
                phone=form.phone.data
            )
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('main.index'))
        elif user_name:
            flash('이미 존재하는 이름입니다.')
        else:
            flash('이미 존재하는 이메일입니다.')

    return render_template('auth/signup.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = UserLoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        error = None
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            error = '존재하지 않는 이메일입니다.'
        elif not check_password_hash(user.password, form.password.data):
            error = '비밀번호가 올바르지 않습니다.'
        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('main.index'))
        else:
            flash(error)
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))



#라우팅 함수보다 먼저 실행하는 함수
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)

@bp.route('/find_id', methods=['GET', 'POST'])
def find_id():
    form = FindIdForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            flash(f"찾으시는 이메일은 [{user.email}] 입니다.")
            return redirect(url_for('auth.login'))
        else:
            flash("해당 이름으로 가입된 이메일이 없습니다.")
    return render_template('auth/find_id.html', form=form)

@bp.route('/find_password', methods=['GET', 'POST'])
def find_password():
    form = ResetPasswordForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data, email=form.email.data).first()
        if user:
            # 비밀번호 해시화하여 업데이트
            user.password = generate_password_hash(form.password1.data)
            db.session.commit()
            flash("비밀번호가 성공적으로 변경되었습니다. 다시 로그인 해주세요.")
            return redirect(url_for('auth.login'))
        else:
            flash("입력하신 정보와 일치하는 사용자가 없습니다.")
    return render_template('auth/find_password.html', form=form)
# 카카오 구글 로그인 추가
# OAuth 설정
# oauth = OAuth()
#
# # 구글 설정
# google = oauth.register(
#     name='google',
#     client_id='YOUR_GOOGLE_CLIENT_ID',
#     client_secret='YOUR_GOOGLE_CLIENT_SECRET',
#     access_token_url='https://accounts.google.com/o/oauth2/token',
#     access_token_params=None,
#     authorize_url='https://accounts.google.com/o/oauth2/auth',
#     authorize_params=None,
#     api_base_url='https://www.googleapis.com/oauth2/v1/',
#     userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
#     client_kwargs={'scope': 'openid email profile'},
# )
#
# # 카카오 설정
# kakao = oauth.register(
#     name='kakao',
#     client_id='YOUR_KAKAO_CLIENT_ID',
#     client_secret='YOUR_KAKAO_CLIENT_SECRET',  # 필요 시 설정
#     authorize_url='https://kauth.kakao.com/oauth/authorize',
#     access_token_url='https://kauth.kakao.com/oauth/token',
#     api_base_url='https://kapi.kakao.com/v2/',
#     client_kwargs={'scope': 'account_email profile_nickname'},
# )
#
#
# # 구글 로그인 라우트
# @bp.route('/login/google')
# def google_login():
#     redirect_uri = url_for('auth.google_authorize', _external=True)
#     return google.authorize_redirect(redirect_uri)
#
#
# @bp.route('/login/google/authorize')
# def google_authorize():
#     token = google.authorize_access_token()
#     resp = google.get('userinfo')
#     user_info = resp.json()
#     # user_info['email'] 등을 사용하여 DB에서 사용자 확인 후 로그인 처리 [cite: 12, 14]
#     return login_social_user(user_info['email'])
#
#
# # 공통 소셜 로그인 처리 함수
# def login_social_user(email):
#     user = User.query.filter_by(email=email).first()
#     if not user:
#         # 가입되지 않은 경우 회원가입 페이지로 유도하거나 자동 가입 처리
#         flash("소셜 계정으로 가입된 정보가 없습니다. 회원가입을 먼저 진행해 주세요.")
#         return redirect(url_for('auth.signup'))
#
#     session.clear()
#     session['user_id'] = user.id
#     return redirect(url_for('main.index'))