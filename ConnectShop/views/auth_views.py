import functools
import requests

from datetime import datetime, timedelta, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from ConnectShop import db
from ConnectShop.forms import UserCreateForm, UserLoginForm, FindIdForm, ResetPasswordForm
from ConnectShop.models import User, Coupon, Order, OrderItem, Product, WithdrawnEmail

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
    # ✅ 쿠폰 개수
    coupon_count = len(getattr(g.user, 'coupons', []) or [])

    # ✅ 배송중 주문 개수
    shipping_count = (
        Order.query
        .filter(
            Order.user_id == g.user.id,
            Order.status == '배송중'
        )
        .count()
    )

    # ✅ 구매확정된 "상품 목록"
    confirmed_products = (
        db.session.query(Product)
        .join(OrderItem, Product.id == OrderItem.product_id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(
            Order.user_id == g.user.id,
            Order.status == '구매확정'
        )
        .order_by(Order.order_date.desc())
        .distinct()
        .limit(6)
        .all()
    )

    return render_template(
        'auth/mypage.html',
        user=g.user,
        coupon_count=coupon_count,
        shipping_count=shipping_count,
        confirmed_products=confirmed_products
    )


@bp.route('/orders')
@login_required
def cart_list():
    return render_template('order/cart_list.html')


@bp.route('/withdraw', methods=['POST'])
@login_required
def withdraw():
    if g.user:
        email = (g.user.email or "").strip().lower()
        now = datetime.now(timezone.utc)

        # 1) 탈퇴 이메일 기록 (재가입 방지용)
        record = WithdrawnEmail.query.filter_by(email=email).first()
        if record:
            record.withdrawn_at = now
        else:
            db.session.add(WithdrawnEmail(email=email, withdrawn_at=now))

        # 2) 쿠폰 먼저 삭제 (NOT NULL user_id 이슈 방지)
        for coupon in getattr(g.user, "coupons", []):
            db.session.delete(coupon)

        # 3) 1:1 관계 benefit 삭제
        if hasattr(g.user, 'benefit') and g.user.benefit:
            db.session.delete(g.user.benefit)

        # 4) 회원 삭제
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

    issued_map = session.get('coupon_issued_map', {}) or {}

    now = datetime.now(timezone.utc)
    expire_delta = timedelta(days=7)

    available_coupons = []
    used_coupons = []

    for c in raw_coupons:
        # 3) 이 쿠폰이 "이후 발급"이라 세션에 발급시각이 있으면 → 만료 체크
        issued_raw = issued_map.get(str(c.id))  # 쿠폰 id를 키로 사용
        expires_at = None
        is_expired = False

        if issued_raw:
            try:
                issued_at = datetime.fromisoformat(issued_raw)
                expires_at = issued_at + expire_delta
                is_expired = now > expires_at
            except ValueError:
                pass

        # 4) 템플릿에서 보여주고 싶으면 임시 속성으로 붙이기(선택)
        c.expires_at = expires_at
        c.is_expired = is_expired

        # 5) 분류: 사용했거나 만료면 used, 아니면 available
        if getattr(c, "is_used", False) or is_expired:
            used_coupons.append(c)
        else:
            available_coupons.append(c)

    # 3. 정리된 데이터만 템플릿으로 전달
    return render_template(
        'auth/coupons.html',
        available_coupons=available_coupons,
        used_coupons=used_coupons
    )


@bp.route('/get-welcome-coupon', methods=['POST'])
@login_required
def get_welcome_coupon():
    # 1. 중복 발급 확인 (계정당 1회 제한)
    # 기존에 발급받은 쿠폰이 하나라도 있다면 발급하지 않음
    if g.user.coupons:
        flash("이미 쿠폰을 발급받으셨거나 보유 중입니다. (계정당 1회 참여 가능)")
        return redirect(url_for('auth.coupons'))

    # 2. 멤버십 상태에 따른 금액 결정
    if g.user.is_membership:
        amount = 3000
        msg = "멤버십 전용 3,000원 쿠폰이 발급되었습니다!"
    else:
        amount = 1000
        msg = "신규 가입 축하 1,000원 쿠폰이 발급되었습니다!"

    # 3. 쿠폰 데이터 생성 및 저장
    new_coupon = Coupon(
        user_id=g.user.id,
        discount_amount=amount,
        is_used=False
    )

    db.session.add(new_coupon)
    db.session.commit()

    issued_map = session.get('coupon_issued_map', {}) or {}
    issued_map[str(new_coupon.id)] = datetime.now(timezone.utc).isoformat()
    session['coupon_issued_map'] = issued_map
    session.modified = True

    flash(msg)
    return redirect(url_for('auth.coupons'))



@bp.route('/me', methods=['GET', 'POST'])
@login_required
def me():
    from ConnectShop.forms import UserUpdateForm
    form = UserUpdateForm(obj=g.user)

    # 쿠폰 개수
    coupon_count = len(g.user.coupons) if hasattr(g.user, 'coupons') else 0

    # 최근 주문 정보
    last_order = Order.query.filter_by(user_id=g.user.id).order_by(Order.order_date.desc()).first()
    address_info = last_order.address if last_order else "주문 이력이 없습니다."
    payment_info = last_order.payment_method if last_order else "등록된 수단 없음"

    if request.method == 'POST' and form.validate_on_submit():
        # 🔥 phone 수정 금지 → phone 업데이트 제거
        db.session.commit()
        flash("정보가 수정되었습니다.")
        return redirect(url_for('auth.me'))

    return render_template(
        'auth/me.html',
        user=g.user,
        form=form,
        address=address_info,
        payment_method=payment_info,
        coupon_count=coupon_count
    )





#카카오 로그인
KAKAO_CLIENT_ID = "edc2045d293aaefae2c494a92245c19a"
KAKAO_REDIRECT_URI = "http://127.0.0.1:5000/auth/kakao/callback"



@bp.route('/kakao/login')
def kakao_login():
    target_url = (
        "https://kauth.kakao.com/oauth/authorize"
        f"?client_id={KAKAO_CLIENT_ID}"
        f"&redirect_uri={KAKAO_REDIRECT_URI}"
        "&response_type=code"
    )
    return redirect(target_url)


@bp.route('/kakao/callback')
def kakao_callback():
    code = request.args.get("code")
    if not code:
        return "No code", 400

    token_res = requests.post(
        "https://kauth.kakao.com/oauth/token",
        headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"},
        data={
            "grant_type": "authorization_code",
            "client_id": KAKAO_CLIENT_ID,
            "redirect_uri": KAKAO_REDIRECT_URI,
            "code": code,
        },
    )
    token_json = token_res.json()
    if "error" in token_json:
        return f"token error: {token_json}", 400

    access_token = token_json.get("access_token")

    user_res = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    user_info = user_res.json()


    # 카카오에서 제공하는 고유 ID 및 이메일 추출
    kakao_id = str(user_info.get("id"))
    kakao_account = user_info.get("kakao_account")
    email = kakao_account.get("email") if kakao_account else f"{kakao_id}@kakao.com"
    nickname = user_info.get("properties", {}).get("nickname", "카카오유저")

    # [C] DB 연동 (기존 가입 여부 확인)
    user = User.query.filter_by(email=email).first()

    if not user:
        # 가입된 적이 없으면 새 유저 생성
        user = User(
            email=email,
            username=nickname,
            password='social_login_no_password',
            phone=f"010-0000-{kakao_id[-4:]}",  # 카카오 ID 뒷자리를 활용해 임시 번호 생성
            is_membership=False
        )
        db.session.add(user)
        db.session.commit()

    # [D] 세션 로그인 처리

    session.clear()
    session['user_id'] = user.id
    print(f"로그인 성공! 세션에 저장된 ID: {session.get('user_id')}")# DB에 저장된 유저의 고유 ID를 세션에 기록
    return redirect(url_for('main.index'))