import base64
import requests

from datetime import timedelta, datetime
from flask import Blueprint, render_template, redirect, url_for, session, g, flash, jsonify, request

from ConnectShop import db
from ConnectShop.models import Cart, Product, Order, OrderItem, Coupon, ProductOption
from ConnectShop.views.auth_views import login_required, cart_list

bp = Blueprint('order', __name__, url_prefix='/order')



# --- Helper Functions ---
def get_guest_cart():
    return session.get('guest_cart', [])


def save_guest_cart(cart):
    session['guest_cart'] = cart
    session.modified = True


from types import SimpleNamespace


def calculate_extra_price(product_id, selected_options):
    """
    사용자가 선택한 전체 옵션 문자열 안에
    DB에 등록된 옵션명(oname)이 포함되어 있는지 대조하여 추가금을 합산합니다.
    """
    if not selected_options:
        return 0

    # 해당 상품의 모든 옵션을 DB에서 가져옴
    all_options = ProductOption.query.filter_by(product_id=product_id).all()
    total_extra = 0

    # 예: selected_options가 "용량: 512GB ㅣ 12GB / 색상: 블랙" 일 때
    # DB의 oname인 "512GB ㅣ 12GB"가 포함되어 있는지 체크
    for opt in all_options:
        if opt.oname in selected_options:
            total_extra += opt.add_price
            print(f"--- [매칭성공] {opt.oname}: +{opt.add_price}원")

    return total_extra


def get_cart_items():
    cart_list = []
    if g.user:
        items = Cart.query.filter_by(user_id=g.user.id).all()
        for item in items:
            # DB에서 가져온 원본 텍스트
            raw_opt = item.selected_options if item.selected_options else ""
            extra_price = calculate_extra_price(item.product_id, raw_opt)

            cart_list.append(SimpleNamespace(
                id=item.id,
                # 🌟 HTML이 헤매지 않게 이름을 다 꽂아줍니다.
                selected_options=raw_opt,
                options=raw_opt,
                opt_str=raw_opt,

                price=item.product.price + extra_price,
                product_name=item.product.name,
                image=item.product.image_path,
                quantity=item.quantity,
                product=item.product
            ))
    else:
        # 비회원 로직도 동일하게 'opt_name' 추가
        guest_cart = get_guest_cart()
        for i, item in enumerate(guest_cart):
            product = db.session.get(Product, item['product_id'])
            if product:
                opt_str = item.get('options', '') or item.get('selected_options', '')
                extra_price = calculate_extra_price(product.id, opt_str)

                cart_list.append(SimpleNamespace(
                    id=i,
                    selected_options=opt_str,
                    options=opt_str,
                    price=product.price + extra_price,
                    image=product.image_path,
                    product_name=product.name,
                    quantity=item.get('quantity', 1),
                    product=product
                ))
    return cart_list

def cleanup_old_carts():
    # 현재 시간으로부터 30일 전 시간 계산
    limit_date = datetime.utcnow() - timedelta(days=30)

    # 30일이 지난 회원 장바구니 아이템 삭제
    expired_items = Cart.query.filter(Cart.created_at < limit_date).all()
    for item in expired_items:
        db.session.delete(item)
    db.session.commit()

# --- Routes ---
@bp.route('/list')
def _list():
    if g.user:
        cleanup_old_carts()

    cart_list = get_cart_items()

    if cart_list:
        print(f"--- [최종체크] 첫번째 아이템 옵션: {getattr(cart_list[0], 'selected_options', '없음')}")

    product_total = sum(item.price * item.quantity for item in cart_list)

    shipping_fee = 3000
    if g.user and g.user.is_membership:
        shipping_fee = 0

    final_total = product_total + shipping_fee

    # 2. 반드시 '가공된' cart_list를 템플릿으로 넘깁니다.
    return render_template('order/cart_list.html',
                           cart_list=cart_list,
                           product_total=product_total,
                           shipping_fee=shipping_fee,
                           total_price=final_total)


@bp.route('/add/<int:product_id>', methods=['POST'])
def add(product_id):
    if request.is_json:
        data = request.get_json()
        quantity = int(data.get('quantity', 1))
        # 🌟 .strip()을 추가하여 양끝 공백을 제거합니다.
        selected_options = data.get('options', "").strip()
    else:
        quantity = int(request.form.get('quantity', 1))
        selected_options = request.form.get('options', "").strip()

    # [디버깅] 옵션 문자열이 DB의 것과 완벽히 일치하는지 확인용
    print(f"--- [DEBUG] 처리할 옵션: [{selected_options}]")

    if g.user:
        # DB에서 동일 상품 + 동일 옵션 검색
        cart = Cart.query.filter_by(
            user_id=g.user.id,
            product_id=product_id,
            selected_options=selected_options
        ).first()

        if cart:
            cart.quantity += quantity
        else:
            db.session.add(Cart(
                user_id=g.user.id,
                product_id=product_id,
                quantity=quantity,
                selected_options=selected_options
            ))
        db.session.commit()
    else:
        # 🌟 비로그인(게스트) 장바구니 중복 처리 추가
        guest_cart = get_guest_cart()
        session.permanent = True
        found = False
        for item in guest_cart:
            # 게스트 카트에서도 상품ID와 옵션이 같으면 수량만 추가
            if item['product_id'] == product_id and item.get('options', "").strip() == selected_options:
                item['quantity'] += quantity
                found = True
                break

        if not found:
            guest_cart.append({
                'product_id': product_id,
                'quantity': quantity,
                'options': selected_options
            })
        save_guest_cart(guest_cart)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        current_cart_list = get_cart_items()
        total_count = sum(item.quantity for item in current_cart_list)
        # 옵션가가 포함된 단가(item.price)를 사용하여 합계 계산
        product_total_val = sum(item.price * item.quantity for item in current_cart_list)

        shipping_fee = 3000
        if product_total_val == 0 or (g.user and getattr(g.user, 'is_membership', False)):
            shipping_fee = 0
        final_total = product_total_val + shipping_fee

        return jsonify({
            'success': True,
            'cart_count': total_count,
            'pure_total': "{:,}".format(product_total_val),       # 상품 총액
            'total_price': "{:,}".format(final_total),            # 최종 결제 예정 금액
            'shipping_fee': "{:,}".format(shipping_fee),          # 배송비
            'raw_pure_total': product_total_val,                  # JS 판별용 숫자
            'raw_total_price': final_total                        # JS 판별용 숫자
        })

    return redirect(url_for('order._list'))

@bp.route('/delete_soldout', methods=['POST'])
def delete_soldout():
    cart_list = get_cart_items()
    deleted_count = 0

    if g.user:
        for item in cart_list:
            if item.product.stock <= 0:
                db.session.delete(item)
                deleted_count += 1
        db.session.commit()
    else:
        new_guest_cart = [
            item for item in get_guest_cart()
            if db.session.get(Product, item['product_id']).stock > 0
        ]
        deleted_count = len(get_guest_cart()) - len(new_guest_cart)
        save_guest_cart(new_guest_cart)

    if deleted_count > 0:
        flash(f"품절된 상품 {deleted_count}건을 삭제했습니다.")
    else:
        flash("삭제할 품절 상품이 없습니다.")

    return redirect(url_for('order._list'))


@bp.route('/delete_selected', methods=['POST'])
def delete_selected():
    # HTML에서 넘어온 선택된 ID 리스트 (cart_id 또는 guest_index)
    selected_ids = request.form.getlist('selected_ids', type=int)

    if not selected_ids:
        flash("삭제할 상품을 선택해주세요.")
        return redirect(url_for('order._list'))

    if g.user:
        # 🌟 회원: Cart 테이블의 PK(id)가 선택된 리스트에 포함된 것만 삭제
        # product_id가 아닌 id로 필터링해야 정확히 선택한 항목만 지워집니다.
        Cart.query.filter(
            Cart.user_id == g.user.id,
            Cart.id.in_(selected_ids)
        ).delete(synchronize_session=False)
        db.session.commit()
    else:
        # 🌟 비회원: 선택된 인덱스(selected_ids)를 제외하고 새로운 리스트 생성
        guest_cart = get_guest_cart()
        # 선택되지 않은(리스트에 없는) 인덱스의 아이템들만 남깁니다.
        new_guest_cart = [
            item for idx, item in enumerate(guest_cart)
            if idx not in selected_ids
        ]
        save_guest_cart(new_guest_cart)

    flash(f"선택하신 {len(selected_ids)}개의 상품을 삭제했습니다.")
    return redirect(url_for('order._list'))


@bp.route('/modify/<int:cart_id>/<string:action>', methods=['POST', 'GET'])
def modify(cart_id, action):
    new_quantity = 0
    is_deleted = False

    if g.user:
        # 1. 회원: DB의 Primary Key(cart_id)로 조회
        cart_item = db.session.get(Cart, cart_id)
        if cart_item and cart_item.user_id == g.user.id:
            if action in ['inc', 'increase']:
                cart_item.quantity += 1
            elif action in ['dec', 'decrease']:
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                else:
                    db.session.delete(cart_item)
                    is_deleted = True
            db.session.commit()
            new_quantity = 0 if is_deleted else cart_item.quantity
    else:
        # 2. 비회원: 세션 리스트의 인덱스(cart_id) 활용
        guest_cart = session.get('guest_cart', [])
        if 0 <= cart_id < len(guest_cart):
            item = guest_cart[cart_id]
            if action in ['inc', 'increase']:
                item['quantity'] += 1
            elif action in ['dec', 'decrease']:
                if item['quantity'] > 1:
                    item['quantity'] -= 1
                else:
                    guest_cart.pop(cart_id)  # 리스트에서 제거
                    is_deleted = True

            session['guest_cart'] = guest_cart
            session.modified = True
            new_quantity = 0 if is_deleted else item['quantity']

        # --- 금액 재계산 영역 ---
    cart_list = get_cart_items()
    pure_total = sum(item.price * item.quantity for item in cart_list)
    total_count = sum(item.quantity for item in cart_list)


    unit_price = 0
    if not is_deleted:
        if g.user:
            # 회원은 DB의 PK(cart_id)와 객체의 id를 비교
            current_item = next((i for i in cart_list if i.id == cart_id), None)
        else:
            # 비회원은 SimpleNamespace에 담긴 id(인덱스)와 cart_id를 비교
            current_item = next((i for i in cart_list if getattr(i, 'id', None) == cart_id), None)

        # [중요] 여기서 옵션가가 포함된 item.price를 가져와야 합니다.
        unit_price = current_item.price if current_item else 0

    shipping_fee = 3000
    if pure_total == 0 or (g.user and getattr(g.user, 'is_membership', False)):
        shipping_fee = 0

    final_total = pure_total + shipping_fee

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'new_quantity': new_quantity,
            'is_deleted': is_deleted,
            'item_unit_price': format(unit_price, ','), # 이 이름이 JS와 매칭됩니다
            'item_total': format(unit_price * new_quantity, ','),
            'pure_total': format(pure_total, ','),
            'total_price': format(final_total, ','),
            'cart_count': total_count,
        })

    return redirect(request.referrer or url_for('order._list'))


@bp.route('/delete/<int:cart_id>')
def delete(cart_id):
    if g.user:
        cart_item = db.session.get(Cart, cart_id)
        if cart_item and cart_item.user_id == g.user.id:
            db.session.delete(cart_item)
            db.session.commit()
    else:
        guest_cart = get_guest_cart()
        if 0 <= cart_id < len(guest_cart):
            guest_cart.pop(cart_id)
            save_guest_cart(guest_cart)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # 🌟 삭제 후 남은 아이템들로 합계를 다시 계산합니다.
        cart_list = get_cart_items()
        pure_total = sum(item.price * item.quantity for item in cart_list)
        total_count = sum(item.quantity for item in cart_list)

        # 배송비 로직 (3,000원 혹은 멤버십 0원)
        shipping_fee = 3000
        if pure_total == 0 or (g.user and getattr(g.user, 'is_membership', False)):
            shipping_fee = 0

        return jsonify({
            "success": True,
            "pure_total": format(pure_total, ','),       # 천단위 콤마 문자열
            "total_price": format(pure_total + shipping_fee, ','),
            "cart_count": total_count,
            "raw_pure_total": pure_total,                # 배송비 판별용 숫자
            "raw_total_price": pure_total + shipping_fee  # 배송비 판별용 숫자
        })

    return redirect(url_for('order._list'))


@bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    # 1. 사용자가 결제창에서 입력한 배송지 정보를 세션에 저장 (POST 요청 시)
    if request.method == 'POST':
        session['temp_order_info'] = {
            'recipient': request.form.get('recipient'),
            'phone': request.form.get('phone'),
            'address': f"{request.form.get('address')} {request.form.get('address_detail')}"
        }

    # 2. 어떤 상품을 결제할지 결정 (바로구매 vs 장바구니)
    is_direct = request.args.get('direct_buy') == 'true'

    # 🌟 [수정] 상세페이지에서 넘어온 쿠폰 ID 혹은 세션에 저장된 쿠폰 ID를 가져옵니다.
    coupon_id = request.args.get('coupon_id') or session.get('applied_coupon_id')

    if is_direct:
        # [바로 구매] 상세 페이지에서 넘어온 단일 상품 정보로 리스트 구성
        p_id = request.args.get('product_id', type=int)
        qty = request.args.get('quantity', type=int, default=1)

        product = db.session.get(Product, p_id)
        if not product:
            flash("존재하지 않는 상품입니다.")
            return redirect(url_for('main.index'))

        cart_list = [SimpleNamespace(product=product, quantity=qty, product_id=p_id)]

        # 🌟 [수정] 적용된 쿠폰 ID가 있다면 세션에 확실히 저장합니다.
        if coupon_id:
            session['applied_coupon_id'] = coupon_id
    else:
        # [장바구니 구매] 기존 방식대로 장바구니 DB에서 가져옴
        cart_list = get_cart_items()

    # 3. 데이터 유무 및 재고 검증
    if not cart_list:
        flash("결제할 상품이 없습니다.")
        return redirect(url_for('order._list'))

    for item in cart_list:
        if item.product.stock < item.quantity:
            flash(f"상품 '{item.product.name}'의 재고가 부족합니다. (현재 재고: {item.product.stock}개)")
            return redirect(url_for('order._list'))

    # 4. 금액 계산 및 렌더링 준비
    now_ts = datetime.now().strftime('%Y%m%d%H%M%S')
    available_coupons = []
    if g.user:
        available_coupons = Coupon.query.filter_by(user_id=g.user.id, is_used=False).all()

    product_total = sum(item.price * item.quantity for item in cart_list)
    shipping_fee = 0 if (g.user and g.user.is_membership) else 3000
    final_total = product_total + shipping_fee

    return render_template('order/checkout.html',
                           cart_list=cart_list,
                           total_price=final_total,
                           product_total=product_total,
                           shipping_fee=shipping_fee,
                           available_coupons=available_coupons,
                           now_ts=now_ts,
                           # 🌟 [추가] 템플릿에서 쓸 수 있도록 쿠폰 ID를 넘겨줍니다.
                           pre_selected_coupon_id=coupon_id)


@bp.route('/save_temp_info', methods=['POST'])
def save_temp_info():
    data = request.get_json()

    print("=" * 50)
    print(f"브라우저에서 넘어온 데이터: {data}")

    # JS에서 보낸 적립금이 있다면 그걸 쓰고, 없으면 0으로 저장
    reward_point = data.get('reward_point', 0)
    session['calculated_reward_point'] = reward_point

    print(f"세션에 저장될 적립금: {session['calculated_reward_point']}")
    print("=" * 50)

    # 1. 기존 배송 정보 저장
    session['temp_recipient'] = data.get('recipient')
    session['temp_phone'] = data.get('phone')
    session['temp_address'] = data.get('address')
    session['temp_memo'] = data.get('memo')
    session['cash_receipt_apply'] = data.get('cash_receipt_apply', False)
    session['cash_receipt_type'] = data.get('cash_receipt_type')
    session['cash_receipt_number'] = data.get('cash_receipt_number')

    # 2. 쿠폰 및 적립금 사전 계산 (박제 로직)
    coupon_id = data.get('coupon_id')
    session['applied_coupon_id'] = coupon_id  # 세션에 쿠폰 ID 고정

    # [중요] 장바구니 상품 총액 (get_cart_items 활용)
    cart_items = get_cart_items()
    pure_product_total = sum(item.price * item.quantity for item in cart_items)

    # 쿠폰 할인액 계산
    discount_val = 0
    if coupon_id and g.user:
        coupon = db.session.get(Coupon, coupon_id)
        if coupon and not coupon.is_used:
            discount_val = coupon.discount_amount

    return jsonify({
        "success": True,
        "debug_reward": reward_point  # 확인용 (생략 가능)
    })


@bp.route('/success')
def success():
    # --- [데이터 수집] ---
    payment_type = request.args.get('paymentType')
    payment_key = request.args.get('paymentKey')
    order_id = request.args.get('orderId')
    amount = request.args.get('amount')

    # --- [변수 초기화] --- 🌟 무조건 맨 위에서 선언하세요!
    cart_items = get_cart_items() # 함수 시작하자마자 장바구니부터 챙깁니다.
    applied_coupon = None
    coupon_id = session.get('applied_coupon_id')
    reward_point = session.get('calculated_reward_point', 0)
    is_success = False
    res_data = {}

    # --- [결제 승인 로직] ---
    if payment_type == 'VBANK':
        is_success = True
        res_data = {'method': '무통장입금'}
    else:
        secret_key = "test_gsk_docs_OaPz8L5KdmQXkzRz3y47BMw6" + ":"
        encoded_key = base64.b64encode(secret_key.encode()).decode()
        url = "https://api.tosspayments.com/v1/payments/confirm"
        headers = {"Authorization": f"Basic {encoded_key}", "Content-Type": "application/json"}

        try:
            response = requests.post(url, json={
                "paymentKey": payment_key, "orderId": order_id, "amount": amount
            }, headers=headers)
            res_data = response.json()
            if response.status_code == 200:
                is_success = True
            else:
                flash(f"결제 승인 실패: {res_data.get('message')}")
                return redirect(url_for('order.checkout'))
        except Exception as e:
            flash(f"통신 오류: {str(e)}")
            return redirect(url_for('order.checkout'))

    # --- [결제 성공 후 DB 작업] ---
    if is_success:
        # 1. 쿠폰 정보 확보
        if coupon_id:
            applied_coupon = db.session.get(Coupon, coupon_id)

        # 2. 적립금 재확인 (세션 유실 대비 & 14,999P 방멸 로직)
        if reward_point == 0 and g.user and g.user.is_membership:
            pure_total = sum(item.price * item.quantity for item in cart_items)
            discount_val = applied_coupon.discount_amount if applied_coupon else 0
            # 🌟 여기서 14,999P가 안 나오게 정확히 0.03(3%)을 곱합니다.
            reward_point = int((pure_total - discount_val) * 0.03)

        # 3. 주문(Order) 데이터 생성
        order = Order(
            user_id=g.user.id if g.user else None,
            recipient=session.get('temp_recipient'),
            phone=session.get('temp_phone'),
            address=session.get('temp_address'),
            memo=session.get('temp_memo'),
            total_price=int(amount),
            reward_point=reward_point,
            is_point_paid=False,
            payment_method=res_data.get('method', '카드/간편결제'),
            status='결제완료' if payment_type != 'VBANK' else '입금대기',
            coupon_id=coupon_id,
            cash_receipt_apply=session.get('cash_receipt_apply', False),
            cash_receipt_type=session.get('cash_receipt_type'),
            cash_receipt_number=session.get('cash_receipt_number')
        )

        # 4. 쿠폰 사용 처리
        if applied_coupon:
            applied_coupon.is_used = True
            applied_coupon.used_date = datetime.now()

        db.session.add(order)
        db.session.flush() # order.id 생성을 위해 flush

        # 5. 주문 상세 내역 및 재고 차감 (이제 cart_items 에러 절대 안 남)
        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product.id,
                quantity=item.quantity,
                price=item.price,
                selected_options=getattr(item, 'selected_options', '')
            )
            db.session.add(order_item)

            product = db.session.get(Product, item.product.id)
            if product:
                product.stock -= item.quantity

        # 6. 장바구니 비우기 및 세션 정리
        if g.user:
            Cart.query.filter_by(user_id=g.user.id).delete()
        else:
            session.pop('guest_cart', None)

        # 사용한 세션 키 정리
        keys_to_pop = ['applied_coupon_id', 'calculated_reward_point', 'temp_recipient',
                       'temp_phone', 'temp_address', 'temp_memo', 'cash_receipt_apply',
                       'cash_receipt_type', 'cash_receipt_number']
        for key in keys_to_pop:
            session.pop(key, None)

        db.session.commit()
        return render_template('order/order_complete.html', order=order, order_id=order.id)

    else:
        flash("결제에 실패하였습니다.")
        return redirect(url_for('order.checkout'))

@bp.route('/my_orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=g.user.id).order_by(Order.order_date.desc()).all()

    pay_done = [o for o in orders if getattr(o, 'status', '결제완료') == '결제완료']
    ready = [o for o in orders if getattr(o, 'status', None) == '배송준비중']
    shipping = [o for o in orders if getattr(o, 'status', None) == '배송중']
    shipped = [o for o in orders if getattr(o, 'status', None) == '배송완료']

    return render_template('order/mypage_order_list.html',
                           order_list=orders,
                           pay_count=len(pay_done),
                           ready_count=len(ready),
                           ship_count=len(shipping),
                           done_count=len(shipped))





@bp.route('/find_guest_order', methods=['GET', 'POST'])
def find_guest_order():
    if request.method == 'POST':
        recipient = request.form.get('recipient')
        phone = request.form.get('phone')

        order_list = Order.query.filter(
            Order.user_id == None,
            Order.recipient == recipient,
            Order.phone == phone
        ).order_by(Order.order_date.desc()).all()

        if order_list:
            session['guest_auth_name'] = recipient
            session['guest_auth_phone'] = phone

            return render_template('order/order_list_history.html', order_list=order_list)
        else:
            flash("일치하는 주문 정보가 없습니다.")

    return render_template('order/guest_order_find.html')


@bp.route('/detail/<int:order_id>')
def order_detail(order_id):
    order = db.session.get(Order, order_id)

    if not order:
        flash("존재하지 않는 주문입니다.")
        return redirect(url_for('main.index'))

    # [권한 체크]
    if g.user:
        if order.user_id != g.user.id:
            flash("접근 권한이 없습니다.")
            return redirect(url_for('order.my_orders'))
    else:
        auth_name = session.get('guest_auth_name')
        auth_phone = session.get('guest_auth_phone')

        if not (auth_name == order.recipient and auth_phone == order.phone):
            flash("비회원 주문 조회 후 이용 가능합니다.")
            return redirect(url_for('order.find_guest_order'))

    can_refund = False
    if order.status in ['배송중', '배송완료']:
        if datetime.now() <= order.order_date + timedelta(days=14):
            can_refund = True

    return render_template('order/order_detail.html', order=order, can_refund=can_refund)


@bp.route('/order/cancel/<int:order_id>', methods=['POST'])
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)

    is_owner = False

    if g.user:
        if order.user_id == g.user.id:
            is_owner = True
    else:
        guest_phone = request.form.get('phone')
        if order.phone == guest_phone:
            is_owner = True

    if not is_owner:
        flash("취소 권한이 없습니다. 정보가 일치하는지 확인하세요.")
        return redirect(request.referrer or url_for('main.index'))

    if order.status in ['결제완료', '입금대기']:
        for item in order.items:
            product = Product.query.get(item.product_id)
            if product:
                product.stock += item.quantity

        if hasattr(order, 'coupon_id') and order.coupon_id:
            coupon = Coupon.query.get(order.coupon_id)
            if coupon:
                coupon.is_used = False
                coupon.used_date = None

        order.status = '주문취소'
        db.session.commit()
        flash(f"주문 #{order_id}번 건이 정상적으로 취소되었습니다.")
    else:
        flash(f"현재 상태('{order.status}')에서는 취소할 수 없습니다. 이미 배송 중이거나 취소된 주문인지 확인해주세요.")

    return redirect(url_for('order.order_detail', order_id=order_id))


@bp.route('/my_cancel_list')
@login_required
def my_cancel_list():
    # 1. 현재 로그인한 사용자의 최근 3개월 주문 내역 조회
    three_months_ago = datetime.now() - timedelta(days=90)
    orders = Order.query.filter(
        Order.user_id == g.user.id,
        Order.order_date >= three_months_ago
    ).all()

    # 2. 취소 또는 반품 상태가 있는 아이템만 추출 (교환 제외)
    cancel_items = []
    for order in orders:
        for item in order.items:
            # 주문 전체가 '주문취소' 상태이거나,
            # 아이템 개별 상태(status)가 존재하면서 '교환'이 포함되지 않은 경우만 추가
            if order.status == '주문취소' or (item.status and '교환' not in item.status):
                item.parent_order = order
                cancel_items.append(item)

    # 3. 최신 주문 날짜 순으로 정렬
    cancel_items.sort(key=lambda x: x.parent_order.order_date, reverse=True)

    return render_template('order/mypage_cancel_list.html', cancel_items=cancel_items)


@bp.route('/confirm_purchase/<int:order_id>', methods=['POST'])
@login_required
def confirm_purchase(order_id):
    order = Order.query.get_or_404(order_id)

    if order.user_id != g.user.id:
        return jsonify({"success": False, "message": "권한이 없습니다."})

    if order.status == '배송완료':
        order.status = '구매확정'

        if not order.is_point_paid and order.reward_point > 0:
            g.user.point += order.reward_point
            order.is_point_paid = True

        db.session.commit()
        flash(f"구매가 확정되었습니다. {order.reward_point}원이 적립되었습니다.")
    else:
        flash("현재 상태에서는 구매 확정이 불가능합니다.")

    return redirect(url_for('order.my_orders'))


import requests


@bp.route('/tracking/<int:order_id>')
def tracking(order_id):
    order = Order.query.get_or_404(order_id)

    if g.user:
        if order.user_id != g.user.id:
            flash("접근 권한이 없습니다.")
            return redirect(url_for('order.my_orders'))
    else:
        auth_name = session.get('guest_auth_name')
        auth_phone = session.get('guest_auth_phone')

        if not (auth_name == order.recipient and auth_phone == order.phone):
            flash("비회원 주문 조회 후 이용 가능합니다.")
            return redirect(url_for('order.find_guest_order'))

    carrier_map = {
        'CJ대한통운': 'kr.cjlogistics',
        '우체국택배': 'kr.epost',
        '한진택배': 'kr.hanjin',
        '롯데택배': 'kr.lotteglogis',
        '로젠택배': 'kr.logen'
    }

    c_company = order.courier_company.strip() if order.courier_company else 'CJ대한통운'
    t_number = order.tracking_number.strip() if order.tracking_number else ''

    carrier_id = carrier_map.get(order.courier_company.strip(), 'kr.cjlogistics')

    api_url = f"https://tracker.delivery/v1/tracks/{carrier_id}/{order.tracking_number}"

    tracking_info = None
    if t_number:
        try:
            response = requests.get(api_url, timeout=5)
            print(f"--- API 응답 확인 ---")
            print(f"URL: {api_url}")
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                tracking_info = response.json()
                print(f"JSON Data: {tracking_info}")
            else:
                tracking_info = None
        except Exception as e:
            print(f"Error: {e}")
            tracking_info = None

    return render_template('order/tracking.html', order=order, info=tracking_info)


@bp.route('/update_address/<int:order_id>', methods=['POST'])
def update_address(order_id):
    order = Order.query.get_or_404(order_id)

    is_owner = False
    if g.user:
        if order.user_id == g.user.id:
            is_owner = True
    else:
        auth_name = session.get('guest_auth_name')
        auth_phone = session.get('guest_auth_phone')
        if auth_name == order.recipient and auth_phone == order.phone:
            is_owner = True

    if not is_owner:
        flash("배송지 수정 권한이 없습니다.")
        return redirect(url_for('main.index'))

    if order.status == '결제완료':
        recipient = request.form.get('recipient')
        phone = request.form.get('phone')
        postcode = request.form.get('postcode', '')
        address = request.form.get('address', '')
        address_detail = request.form.get('address_detail', '')

        full_address = f"[{postcode}] {address} {address_detail}".strip()

        if not recipient or not address:
            flash("이름과 주소는 필수 입력 사항입니다.")
            return redirect(url_for('order.order_detail', order_id=order_id))

        order.recipient = recipient
        order.phone = phone
        order.address = full_address

        db.session.commit()

        if not g.user:
            session['guest_auth_name'] = recipient
            session['guest_auth_phone'] = phone

        flash("배송지 정보가 변경되었습니다.")
    else:
        flash("배송 준비 중이거나 완료된 주문은 주소를 변경할 수 없습니다.")

    return redirect(url_for('order.order_detail', order_id=order_id))


@bp.route('/refund/<int:order_id>/<int:item_id>/<string:type>', methods=['POST', 'GET'])
def refund_request(order_id, item_id, type):
    order = db.session.get(Order, order_id)
    order_item = db.session.get(OrderItem, item_id)

    if not order or not order_item:
        flash("주문 정보를 찾을 수 없습니다.", "danger")
        return redirect(url_for('order.order_detail', order_id=order_id))

    # 1. 환불일 경우: 금액 차감 및 상태 변경
    if type == '환불':
        refund_amount = order_item.price * order_item.quantity
        # 주문의 총 결제 금액에서 환불 상품만큼 차감
        order.total_price = max(0, order.total_price - refund_amount)
        order_item.status = '환불신청'

    # 2. 교환일 경우: 금액 유지 및 상태만 변경
    elif type == '교환':
        order_item.status = '교환신청'

    try:
        db.session.commit()
        flash(f"{type} 신청이 정상적으로 완료되었습니다.", "success")
    except Exception as e:
        db.session.rollback()
        flash("처리 중 오류가 발생했습니다.", "danger")

    return redirect(url_for('order.order_detail', order_id=order_id))

@bp.app_context_processor
def inject_cart_totals():
    cart_list = get_cart_items()

    product_total = sum(item.price * item.quantity for item in cart_list)

    # 템플릿에서 사용할 변수 이름으로 반환
    return dict(
        cart_list=cart_list,
        product_total=product_total
    )

# ==========================================================
# 🌟 마이페이지 - 찜목록 모아보기 라우트
# ==========================================================
@bp.route('/wishlist')
@login_required  # 로그인이 안 되어있으면 자동으로 로그인 창으로 보냄
def wishlist():
    return render_template('order/wishlist.html')