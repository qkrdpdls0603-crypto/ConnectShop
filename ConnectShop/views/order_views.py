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

    all_options = ProductOption.query.filter_by(product_id=product_id).all()
    total_extra = 0

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
            raw_opt = item.selected_options if item.selected_options else ""
            extra_price = calculate_extra_price(item.product_id, raw_opt)

            cart_list.append(SimpleNamespace(
                id=item.id,
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
        guest_cart = get_guest_cart()
        # 🌟 i(인덱스) 대신 실제 item 안에 들어있는 'id'를 사용해야 합니다.
        for item in guest_cart:
            product = db.session.get(Product, item['product_id'])
            if product:
                opt_str = item.get('options', '') or item.get('selected_options', '')
                extra_price = calculate_extra_price(product.id, opt_str)

                cart_list.append(SimpleNamespace(
                    # 🌟 여기를 수정: 세션에 저장된 고유 ID를 그대로 사용
                    # 만약 옛날 데이터라 ID가 없다면, 리스트 인덱스라도 사용하도록 방어 코드 작성
                    id=item.get('id', guest_cart.index(item)),
                    selected_options=opt_str,
                    options=opt_str,
                    price=product.price + extra_price,
                    image=product.image_path,
                    product_name=product.name,
                    quantity=item.get('quantity', 1),
                    product=product
                ))
    return cart_list


# 🌟 팀원분의 장바구니 최적화 로직 유지
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
        selected_options = data.get('options', "").strip()
    else:
        quantity = int(request.form.get('quantity', 1))
        selected_options = request.form.get('options', "").strip()

    print(f"--- [DEBUG] 처리할 옵션: [{selected_options}]")

    if g.user:
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
        guest_cart = get_guest_cart()
        session.permanent = True
        found = False
        for item in guest_cart:
            # options 키값이 delete 로직과 일치하도록 통일 (아래 예시는 options 사용)
            if item['product_id'] == product_id and item.get('options', "").strip() == selected_options:
                item['quantity'] += quantity
                found = True
                break

        if not found:
            guest_cart.append({
                # 🌟 고유 ID 생성 (타임스탬프 활용)
                'id': int(datetime.now().timestamp() * 1000),
                'product_id': product_id,
                'quantity': quantity,
                'options': selected_options
            })
        save_guest_cart(guest_cart)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        current_cart_list = get_cart_items()
        total_count = sum(item.quantity for item in current_cart_list)
        product_total_val = sum(item.price * item.quantity for item in current_cart_list)

        shipping_fee = 3000
        if product_total_val == 0 or (g.user and getattr(g.user, 'is_membership', False)):
            shipping_fee = 0
        final_total = product_total_val + shipping_fee

        return jsonify({
            'success': True,
            'cart_count': total_count,
            'pure_total': "{:,}".format(product_total_val),
            'total_price': "{:,}".format(final_total),
            'shipping_fee': "{:,}".format(shipping_fee),
            'raw_pure_total': product_total_val,
            'raw_total_price': final_total
        })

    return redirect(url_for('order._list'))


@bp.route('/direct_buy/<int:product_id>', methods=['POST'])
def direct_buy(product_id):
    data = request.get_json()
    quantity = int(data.get('quantity', 1))
    options = data.get('options', "").strip()

    # ✅ 장바구니 DB에 넣지 않고 세션에 "나 이거 살거야"라고 표시만 합니다.
    session['direct_order_info'] = {
        'product_id': product_id,
        'quantity': quantity,
        'options': options
    }
    session.modified = True

    return jsonify({
        'success': True,
        'checkout_url': url_for('order.checkout', direct_buy='true')
    })

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
    selected_ids = request.form.getlist('selected_ids', type=int)

    if not selected_ids:
        flash("삭제할 상품을 선택해주세요.")
        return redirect(url_for('order._list'))

    if g.user:
        Cart.query.filter(
            Cart.user_id == g.user.id,
            Cart.id.in_(selected_ids)
        ).delete(synchronize_session=False)
        db.session.commit()
    else:
        guest_cart = get_guest_cart()
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

    try:
        # [수량 조절 로직] - 이 부분은 기존과 동일
        if g.user:
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
            guest_cart = session.get('guest_cart', [])
            if 0 <= cart_id < len(guest_cart):
                target = guest_cart[cart_id]
                if action in ['inc', 'increase']:
                    target['quantity'] += 1
                elif action in ['dec', 'decrease']:
                    if target['quantity'] > 1:
                        target['quantity'] -= 1
                    else:
                        guest_cart.pop(cart_id)
                        is_deleted = True
                session['guest_cart'] = guest_cart
                session.modified = True
                new_quantity = 0 if is_deleted else target['quantity']

        # 🌟 [중요] 여기서부터는 if/else 밖으로 완전히 나와야 합니다!
        cart_list = get_cart_items()
        current_unit_price = 0

        if not is_deleted:
            # get_cart_items에서 계산된 단가를 가져옴 (이미지의 1,690,000원)
            current_item = next((item for item in cart_list if item.id == cart_id), None)
            if current_item:
                current_unit_price = current_item.price

        pure_total = sum(item.price * item.quantity for item in cart_list)
        total_count = sum(item.quantity for item in cart_list)
        shipping_fee = 0 if (g.user and getattr(g.user, 'is_membership', False)) else (3000 if pure_total > 0 else 0)

        # AJAX 요청이면 JSON 응답
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'new_quantity': int(new_quantity),
                'is_deleted': is_deleted,
                'item_total': int(current_unit_price * new_quantity),  # 이미지의 '0원' 부분을 채울 값
                'pure_total': int(pure_total),
                'total_price': int(pure_total + shipping_fee),
                'cart_count': int(total_count)
            })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

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
        new_guest_cart = [item for item in guest_cart if item.get('id') != cart_id]
        save_guest_cart(new_guest_cart)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_list = get_cart_items()
        pure_total = sum(item.price * item.quantity for item in cart_list)
        total_count = sum(item.quantity for item in cart_list)

        shipping_fee = 3000
        if pure_total == 0 or (g.user and getattr(g.user, 'is_membership', False)):
            shipping_fee = 0

        return jsonify({
            "success": True,
            "pure_total": format(pure_total, ','),
            "total_price": format(pure_total + shipping_fee, ','),
            "cart_count": total_count,
            "raw_pure_total": pure_total,
            "raw_total_price": pure_total + shipping_fee
        })

    return redirect(url_for('order._list'))


@bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        session['temp_order_info'] = {
            'recipient': request.form.get('recipient'),
            'phone': request.form.get('phone'),
            'address': f"{request.form.get('address')} {request.form.get('address_detail')}"
        }

    is_direct = request.args.get('direct_buy') == 'true'
    coupon_id = request.args.get('coupon_id') or session.get('applied_coupon_id')

    if is_direct:
        # ✅ 세션에서 즉시구매 정보 가져오기 (보안 및 안정성 강화)
        direct_info = session.get('direct_order_info')
        if not direct_info:
            flash("주문 정보가 없습니다.")
            return redirect(url_for('main.index'))

        product = db.session.get(Product, direct_info['product_id'])
        if not product:
            flash("존재하지 않는 상품입니다.")
            return redirect(url_for('main.index'))

        # ✅ 즉시구매 상품도 옵션 추가 금액을 계산해서 정확한 가격을 책정합니다.
        extra_price = calculate_extra_price(product.id, direct_info['options'])

        # 템플릿이 사용할 수 있게 SimpleNamespace로 포맷팅
        cart_list = [SimpleNamespace(
            product=product,
            quantity=direct_info['quantity'],
            product_id=product.id,
            price=product.price + extra_price,  # 기본가 + 옵션 추가금
            selected_options=direct_info['options'],
            image=product.image_path,
            product_name=product.name
        )]

        # ✅ 안전장치: 혹시 URL로 쿠폰 ID가 넘어왔다면 세션에 저장
        if coupon_id:
            session['applied_coupon_id'] = coupon_id
    else:
        # 일반 장바구니 결제
        cart_list = get_cart_items()

    if not cart_list:
        flash("결제할 상품이 없습니다.")
        return redirect(url_for('order._list'))

    for item in cart_list:
        if item.product.stock < item.quantity:
            flash(f"상품 '{item.product.name}'의 재고가 부족합니다. (현재 재고: {item.product.stock}개)")
            return redirect(url_for('order._list'))

    now_ts = datetime.now().strftime('%Y%m%d%H%M%S')
    available_coupons = []
    if g.user:
        available_coupons = Coupon.query.filter_by(user_id=g.user.id, is_used=False).all()

    product_total = sum(item.price * item.quantity for item in cart_list)
    shipping_fee = 0 if (g.user and g.user.is_membership) else 3000
    final_total = product_total + shipping_fee
    current_order = None

    if g.user:
        current_order = Order.query.filter_by(user_id=g.user.id, status='WAITING').first()

    if not current_order:
        # 주문 번호 생성
        order_number = f"TS{now_ts}{g.user.id if g.user else 'G'}"

        current_order = Order(
            user_id=g.user.id if g.user else None,
            order_number=order_number,
            total_price=final_total,
            status='WAITING',
            recipient='임시',
            phone='010-0000-0000',
            address='임시 주소',
            payment_method='temp'
        )
        db.session.add(current_order)
    else:
        current_order.total_price = final_total
        current_order.order_number = f"TS{now_ts}{g.user.id if g.user else 'G'}"  # 번호도 최신화


    db.session.commit()

    last_order = None
    if g.user:
        last_order = Order.query.filter_by(user_id=g.user.id) \
            .order_by(Order.order_date.desc()) \
            .first()

    return render_template('order/checkout.html',
                           order=current_order,
                           cart_list=cart_list,
                           total_price=final_total,
                           product_total=product_total,
                           shipping_fee=shipping_fee,
                           available_coupons=available_coupons,
                           now_ts=now_ts,
                           pre_selected_coupon_id=coupon_id,
                           last_order=last_order)


# 🌟 [병합 완료] 팀장님의 '사용 포인트' + 팀원분의 '적립금 및 현금영수증' 완벽 통합
@bp.route('/save_temp_info', methods=['POST'])
def save_temp_info():
    data = request.get_json()

    print("=" * 50)
    print(f"브라우저에서 넘어온 통합 데이터: {data}")
    print("=" * 50)

    # 1. 배송 정보
    session['temp_recipient'] = data.get('recipient')
    session['temp_phone'] = data.get('phone')
    session['temp_address'] = data.get('address')
    session['temp_memo'] = data.get('memo')
    
    # 2. 현금영수증 정보 (팀원분)
    session['cash_receipt_apply'] = data.get('cash_receipt_apply', False)
    session['cash_receipt_type'] = data.get('cash_receipt_type')
    session['cash_receipt_number'] = data.get('cash_receipt_number')

    # 3. 쿠폰 및 리워드/포인트 정보 (양측 통합)
    session['applied_coupon_id'] = data.get('coupon_id')
    session['temp_used_point'] = data.get('used_point', 0)  # 팀장님 포인트 사용
    session['calculated_reward_point'] = data.get('reward_point', 0)  # 팀원분 리워드 박제

    return jsonify({"success": True})

#  아래코드의 수정 이전 버전 나중에 충돌 일어날거 같아 주석처리함
# 🌟 [병합 완료] 무통장 분기처리 + 포인트/보너스 처리 완벽 통합!
# @bp.route('/success')
# def success():
#     # --- [데이터 수집] ---
#     payment_type = request.args.get('paymentType')
#     payment_key = request.args.get('paymentKey')
#     order_id = request.args.get('orderId')
#     amount = request.args.get('amount')
#     is_direct = request.args.get('direct_buy') == 'true'
#     # --- [변수 초기화] ---
#     cart_items = get_cart_items()
#     coupon_id = session.get('applied_coupon_id')
#     used_point = int(session.get('temp_used_point', 0))
#     reward_point = int(session.get('calculated_reward_point', 0))
#
#     is_success = False
#     res_data = {}
#     payment_method_used = '무통장입금' # 기본값
#
#     # --- [결제 승인 로직 (팀원 분기처리 적용)] ---
#     if payment_type == 'VBANK':
#         is_success = True
#         payment_method_used = '무통장입금'
#     else:
#         secret_key = "test_gsk_docs_OaPz8L5KdmQXkzRz3y47BMw6" + ":"
#         encoded_key = base64.b64encode(secret_key.encode()).decode()
#         url = "https://api.tosspayments.com/v1/payments/confirm"
#         headers = {"Authorization": f"Basic {encoded_key}", "Content-Type": "application/json"}
#
#         try:
#             response = requests.post(url, json={
#                 "paymentKey": payment_key, "orderId": order_id, "amount": amount
#             }, headers=headers)
#             res_data = response.json()
#             if response.status_code == 200:
#                 is_success = True
#                 payment_method_used = res_data.get('method', '카드/간편결제')
#             else:
#                 flash(f"결제 승인 실패: {res_data.get('message')}")
#                 return redirect(url_for('order.checkout'))
#         except Exception as e:
#             flash(f"통신 오류: {str(e)}")
#             return redirect(url_for('order.checkout'))
#
#     # --- [결제 성공 후 DB 작업 (통합)] ---
#     if is_success:
#         # 1. 쿠폰 처리
#         applied_coupon = None
#         if coupon_id and g.user:
#             applied_coupon = Coupon.query.filter_by(id=coupon_id, user_id=g.user.id, is_used=False).first()
#
#         # 2. 적립금 재확인 및 계좌이체(무통장) 3% 보너스 적용! (팀장님 로직 융합)
#         if payment_method_used in ['계좌이체', '가상계좌', '무통장입금']:
#             bonus_point = int(int(amount) * 0.03)
#             reward_point += bonus_point
#             print(f"--- [보너스 적립] 현금성 결제 3% 추가 적용: +{bonus_point}원")
#
#         # 3. [포인트 차감] 유저 지갑에서 실제로 포인트 빼기
#         if g.user and used_point > 0:
#             actual_used_point = min(g.user.point, used_point)
#             g.user.point -= actual_used_point
#             used_point = actual_used_point
#
#         # 4. 주문(Order) 객체 생성 (현금영수증, 포인트 상태 완벽 기록)
#         order_status = '입금대기' if payment_type == 'VBANK' else '결제완료'
#         order = Order(
#             user_id=g.user.id if g.user else None,
#             recipient=session.get('temp_recipient'),
#             phone=session.get('temp_phone'),
#             address=session.get('temp_address'),
#             memo=session.get('temp_memo'),
#             total_price=int(amount),
#             reward_point=reward_point,
#             is_point_paid=False,
#             payment_method=payment_method_used,
#             status=order_status,
#             coupon_id=coupon_id,
#             used_point=used_point,
#             cash_receipt_apply=session.get('cash_receipt_apply', False),
#             cash_receipt_type=session.get('cash_receipt_type'),
#             cash_receipt_number=session.get('cash_receipt_number')
#         )
#
#         if applied_coupon:
#             applied_coupon.is_used = True
#             applied_coupon.used_date = datetime.now()
#
#         db.session.add(order)
#         db.session.flush() # order.id 생성을 위해 flush
#
#         # 5. 주문 상세 내역(OrderItem) 및 재고 차감
#         for item in cart_items:
#             order_item = OrderItem(
#                 order_id=order.id,
#                 product_id=item.product.id,
#                 quantity=item.quantity,
#                 price=item.price,
#                 selected_options=getattr(item, 'selected_options', '')
#             )
#             db.session.add(order_item)
#
#             product = db.session.get(Product, item.product.id)
#             if product:
#                 product.stock -= item.quantity
#
#         # 6. 장바구니 비우기 및 세션 완전 정리
#         if g.user:
#             Cart.query.filter_by(user_id=g.user.id).delete()
#         else:
#             session.pop('guest_cart', None)
#
#         keys_to_pop = [
#             'applied_coupon_id', 'calculated_reward_point', 'temp_recipient',
#             'temp_phone', 'temp_address', 'temp_memo', 'cash_receipt_apply',
#             'cash_receipt_type', 'cash_receipt_number', 'temp_used_point'
#         ]
#         for key in keys_to_pop:
#             session.pop(key, None)
#
#         db.session.commit()
#         return render_template('order/order_complete.html', order=order, order_id=order.id)
#     else:
#         flash("결제에 실패하였습니다.")
#         return redirect(url_for('order.checkout'))


# 🌟 [최종 통합본] 즉시 구매 분기 + 포인트/보너스/이미지 경로 완벽 대응
@bp.route('/success')
def success():
    # --- [1. 데이터 수집] ---
    payment_type = request.args.get('paymentType')
    payment_key = request.args.get('paymentKey')
    order_id = request.args.get('orderId')
    amount = request.args.get('amount')

    # 즉시 구매 여부 확인 (JS에서 보낸 direct_buy=true 파라미터)
    is_direct = request.args.get('direct_buy') == 'true'

    # --- [2. 주문 상품 데이터 구성 (분기)] ---
    if is_direct:
        # ✅ 즉시 구매 세션에서 정보 추출
        direct_info = session.get('direct_order_info')
        if not direct_info:
            flash("주문 정보가 만료되었습니다. 다시 시도해주세요.")
            return redirect(url_for('main.index'))

        product = db.session.get(Product, direct_info['product_id'])
        if not product:
            flash("존재하지 않는 상품입니다.")
            return redirect(url_for('main.index'))

        extra_price = calculate_extra_price(product.id, direct_info['options'])

        # 템플릿과 로직에서 공통으로 사용할 리스트 생성
        cart_items = [SimpleNamespace(
            product=product,
            quantity=direct_info['quantity'],
            price=product.price + extra_price,
            selected_options=direct_info['options'],
            image=product.image_path,  # 🌟 이미지 에러 방지용
            product_name=product.name
        )]
    else:
        # ✅ 일반 장바구니 결제
        cart_items = get_cart_items()

    # 쿠폰 및 포인트 정보 가져오기
    coupon_id = session.get('applied_coupon_id')
    used_point = int(session.get('temp_used_point', 0))
    reward_point = int(session.get('calculated_reward_point', 0))

    is_success = False
    res_data = {}
    payment_method_used = '무통장입금'

    # --- [3. 결제 승인 로직 (토스 페이먼츠 / 무통장)] ---
    if payment_type == 'VBANK':
        is_success = True
        payment_method_used = '무통장입금'
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
                payment_method_used = res_data.get('method', '카드/간편결제')
            else:
                flash(f"결제 승인 실패: {res_data.get('message')}")
                return redirect(url_for('order.checkout'))
        except Exception as e:
            flash(f"통신 오류: {str(e)}")
            return redirect(url_for('order.checkout'))

    # --- [4. 결제 성공 후 DB 작업] ---
    if is_success:
        # 1) 쿠폰 처리
        applied_coupon = None
        if coupon_id and g.user:
            applied_coupon = Coupon.query.filter_by(id=coupon_id, user_id=g.user.id, is_used=False).first()

        # 2) [보안 체크] 일반 회원임이 확인되면 기본 적립금을 강제로 0으로 초기화 (팀원 로직)
        if not (g.user and g.user.is_membership):
            reward_point = 0
            print("--- [보안 체크] 일반 회원임이 확인되어 기본 적립금을 0원으로 변경합니다.")

        # 3) 현금성 결제 3% 보너스 적립 추가 (팀장 로직)
        if payment_method_used in ['계좌이체', '가상계좌', '무통장입금']:
            bonus_point = int(int(amount) * 0.03)
            reward_point += bonus_point
            print(f"--- [보너스 적립] 현금성 결제 3% 추가 적용: +{bonus_point}원")

        # 4) 사용 포인트 차감
        if g.user and used_point > 0:
            actual_used_point = min(g.user.point, used_point)
            g.user.point -= actual_used_point
            used_point = actual_used_point

        # 5) 주문(Order) 객체 생성
        order_status = '입금대기' if payment_type == 'VBANK' else '결제완료'
        order = Order(
            user_id=g.user.id if g.user else None,
            recipient=session.get('temp_recipient'),
            phone=session.get('temp_phone'),
            address=session.get('temp_address'),
            memo=session.get('temp_memo'),
            total_price=int(amount),
            reward_point=reward_point, # 검증과 보너스가 모두 적용된 최종 적립금
            is_point_paid=False,
            payment_method=payment_method_used,
            status=order_status,
            coupon_id=coupon_id,
            used_point=used_point,
            cash_receipt_apply=session.get('cash_receipt_apply', False),
            cash_receipt_type=session.get('cash_receipt_type'),
            cash_receipt_number=session.get('cash_receipt_number')
        )

        if applied_coupon:
            applied_coupon.is_used = True
            applied_coupon.used_date = datetime.now()

        db.session.add(order)
        db.session.flush()  # order.id 생성을 위해 실행

        # 5) 주문 상세 내역(OrderItem) 및 재고 차감
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

        # 6) [중요] 장바구니 비우기 분기 처리
        if is_direct:
            # 즉시 구매면 임시 세션만 제거
            session.pop('direct_order_info', None)
        else:
            # 장바구니 결제면 DB/세션 장바구니 비우기
            if g.user:
                Cart.query.filter_by(user_id=g.user.id).delete()
            else:
                session.pop('guest_cart', None)

        # 공통 세션 정리
        keys_to_pop = [
            'applied_coupon_id', 'calculated_reward_point', 'temp_recipient',
            'temp_phone', 'temp_address', 'temp_memo', 'cash_receipt_apply',
            'cash_receipt_type', 'cash_receipt_number', 'temp_used_point'
        ]
        for key in keys_to_pop:
            session.pop(key, None)

        db.session.commit()

        # 🌟 'order' 변수가 이 블록 안에서 정의되었으므로 unresolved reference 경고가 사라집니다.
        return render_template('order/order_complete.html', order=order, order_id=order.id)

    else:
        flash("결제 승인 과정에서 문제가 발생했습니다.")
        return redirect(url_for('order.checkout'))




@bp.route('/place_order', methods=['POST'])
def place_order():
    recipient = request.form.get('recipient')
    phone = request.form.get('phone')[:13]
    address = f"{request.form.get('address')} {request.form.get('address_detail')}"
    payment_method = request.form.get('payment_method')

    cart_list = get_cart_items()
    if not cart_list:
        flash("장바구니가 비어 있습니다.")
        return redirect(url_for('main.index'))

    for item in cart_list:
        if item.product.stock < item.quantity:
            flash(f"죄송합니다. '{item.product.name}' 상품의 재고가 부족합니다. (남은 수량: {item.product.stock}개)")
            return redirect(url_for('cart.view_cart'))

    total_price = sum(item.product.price * item.quantity for item in cart_list)

    new_order = Order(
        user_id=g.user.id if g.user else None,
        recipient=recipient,
        phone=phone,
        address=address,
        total_price=total_price,
        payment_method=payment_method,
        status='결제완료'
    )
    db.session.add(new_order)

    for item in cart_list:
        order_item = OrderItem(
            order=new_order,
            product_id=item.product.id,
            quantity=item.quantity,
            price=item.price,
            selected_options=getattr(item, 'selected_options', '')
        )
        db.session.add(order_item)

        product = Product.query.get(item.product.id)
        if product:
            product.stock -= item.quantity

    if g.user:
        Cart.query.filter_by(user_id=g.user.id).delete()
    else:
        session.pop('guest_cart', None)

    db.session.commit()

    flash("주문이 성공적으로 완료되었습니다!")
    return redirect(url_for('order.order_complete', order_id=new_order.id))


@bp.route('/complete/<int:order_id>')
def order_complete(order_id):
    order = db.session.get(Order, order_id)

    if not order:
        return redirect(url_for('main.index'))

    return render_template('order/order_complete.html', order=order)


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

        if g.user and hasattr(order, 'used_point') and order.used_point > 0:
            g.user.point += order.used_point
            print(f"--- [포인트 복구] {order.used_point}원이 다시 반환되었습니다.")

        order.status = '주문취소'
        db.session.commit()
        flash(f"주문 #{order_id}번 건이 정상적으로 취소되었습니다.")
    else:
        flash(f"현재 상태('{order.status}')에서는 취소할 수 없습니다. 이미 배송 중이거나 취소된 주문인지 확인해주세요.")

    return redirect(url_for('order.order_detail', order_id=order_id))


@bp.route('/my_cancel_list')
@login_required
def my_cancel_list():
    three_months_ago = datetime.now() - timedelta(days=90)
    orders = Order.query.filter(
        Order.user_id == g.user.id,
        Order.order_date >= three_months_ago
    ).all()

    cancel_items = []
    for order in orders:
        for item in order.items:
            if order.status == '주문취소' or (item.status and '교환' not in item.status):
                item.parent_order = order
                cancel_items.append(item)

    cancel_items.sort(key=lambda x: x.parent_order.order_date, reverse=True)

    return render_template('order/mypage_cancel_list.html', cancel_items=cancel_items)


@bp.route('/my_return_list')
@login_required
def my_return_list():
    three_months_ago = datetime.now() - timedelta(days=90)
    orders = Order.query.filter(
        Order.user_id == g.user.id,
        Order.order_date >= three_months_ago
    ).all()

    return_items = []
    for order in orders:
        for item in order.items:
            # 🌟 반품, 환불 키워드가 포함된 상태만 추출
            if item.status and any(keyword in item.status for keyword in ['반품', '환불', '교환']):
                item.parent_order = order
                return_items.append(item)

    return_items.sort(key=lambda x: x.parent_order.order_date, reverse=True)
    return render_template('order/mypage_return_list.html', return_items=return_items)


@bp.route('/confirm_purchase/<int:order_id>', methods=['POST'])
@login_required
def confirm_purchase(order_id):
    order = Order.query.get_or_404(order_id)

    if order.user_id != g.user.id:
        return jsonify({"success": False, "message": "권한이 없습니다."})

    is_locked = any(item.status in ['환불신청', '교환신청', '환불완료'] for item in order.items)

    if is_locked:
        flash("교환 또는 환불 신청이 진행 중인 주문은 구매확정이 불가능합니다.")
        return redirect(url_for('order.order_detail', order_id=order_id))

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
            if response.status_code == 200:
                tracking_info = response.json()
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

    if order_item.status in ['환불신청', '환불완료', '교환신청', '교환완료']:
        flash("이미 처리 중이거나 완료된 신청입니다.", "warning")
        return redirect(url_for('order.order_detail', order_id=order_id))

    if type == '환불':
        order_item.status = '환불신청'
        order.status = '환불신청'
    elif type == '교환':
        order_item.status = '교환신청'
        order.status = '교환신청'

    try:
        db.session.commit()
        flash(f"{type} 처리가 정상적으로 완료되었습니다.", "success")
    except Exception as e:
        db.session.rollback()
        flash("처리 중 오류가 발생했습니다.", "danger")

    return redirect(url_for('order.order_detail', order_id=order_id))


@bp.app_context_processor
def inject_cart_totals():
    cart_list = get_cart_items()

    product_total = sum(item.price * item.quantity for item in cart_list)

    return dict(
        cart_list=cart_list,
        product_total=product_total
    )


@bp.route('/wishlist')
@login_required
def wishlist():
    return render_template('order/wishlist.html')

# =======================================================
# 🌟 팀원 로직: 관리자 환불 승인 및 포인트/쿠폰 복구
# =======================================================
@bp.route('/admin/approve_refund/<int:item_id>', methods=['POST'])
def approve_refund(item_id):
    order_item = db.session.get(OrderItem, item_id)
    order = order_item.order

    if order_item.status != '환불신청':
        return jsonify({"success": False, "message": "환불 신청 상태가 아닙니다."})

    # --- [실제 수치 차감 및 복구 시작] ---
    item_total = order_item.price * order_item.quantity

    # 1. 적립금 비례 차감
    total_items_price = sum(item.price * item.quantity for item in order.items)
    if total_items_price > 0:
        refund_ratio = item_total / total_items_price
        order.reward_point = max(0, order.reward_point - int(order.reward_point * refund_ratio))

    # 2. 포인트 반환 및 실제 현금 환불액 계산
    if order.used_point > 0:
        return_point = min(order.used_point, item_total)
        order.user.point += return_point  # 유저에게 포인트 복구
        order.used_point -= return_point
        actual_cash_refund = item_total - return_point
    else:
        actual_cash_refund = item_total

    # 3. 주문 정보 업데이트
    order.total_price = max(0, order.total_price - actual_cash_refund)
    order_item.status = '환불완료'

    # 🌟 4. [쿠폰 복구] 모든 아이템이 '환불완료'인지 체크
    all_refunded = all(item.status == '환불완료' for item in order.items)
    if all_refunded:
        order.status = '환불완료'
        if order.coupon_id:
            coupon = db.session.get(Coupon, order.coupon_id)
            if coupon:
                coupon.is_used = False
                coupon.used_date = None
    else:
        order.status = '부분환불완료'

    db.session.commit()
    return jsonify({"success": True, "message": "환불 처리가 최종 승인되었습니다."})


# =======================================================
# 🌟 팀장님 로직: 마이페이지 구매확정/환불 대상 리스트 조회
# =======================================================
@bp.route('/api/get_delivery_done_items')
@login_required
def get_delivery_done_items():
    # 1. 구매확정 대상 (주문 상태가 '배송완료'인 상품들)
    confirm_targets = OrderItem.query.join(Order).filter(
        Order.user_id == g.user.id,
        Order.status == '배송완료',
        OrderItem.status == None # 아직 아무 처리가 안 된 상품
    ).all()

    # 2. 환불/교환 대상 (이미 배송완료되었거나 결제완료된 건 중 신청 가능한 것)
    claim_targets = OrderItem.query.join(Order).filter(
        Order.user_id == g.user.id,
        Order.status.in_(['배송완료', '배송중']),
        OrderItem.status == None
    ).all()

    return jsonify({
        'confirm_list': [{
            'id': item.id,
            'order_id': item.order_id,
            'name': item.product.name,
            'option': item.selected_options,
            'price': item.price * item.quantity,
            'img': url_for('static', filename='images/menu/' + item.product.image_path)
        } for item in confirm_targets],
        'claim_list': [{
            'id': item.id,
            'order_id': item.order_id,
            'name': item.product.name,
            'price': item.price * item.quantity,
            'img': url_for('static', filename='images/menu/' + item.product.image_path)
        } for item in claim_targets]
    })