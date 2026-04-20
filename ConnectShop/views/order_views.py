import base64
import requests

from datetime import timedelta, datetime
from types import SimpleNamespace
from flask import Blueprint, render_template, redirect, url_for, session, g, flash, jsonify, request

from ConnectShop import db
from ConnectShop.models import Cart, Product, Order, OrderItem, Coupon
from ConnectShop.views.auth_views import login_required, cart_list

bp = Blueprint('order', __name__, url_prefix='/order')



# --- Helper Functions ---
def get_guest_cart():
    return session.get('guest_cart', [])


def save_guest_cart(cart):
    session['guest_cart'] = cart
    session.modified = True


def get_cart_items():
    if g.user:
        return Cart.query.filter_by(user_id=g.user.id).all()

    guest_cart = get_guest_cart()
    cart_list = []
    for item in guest_cart:
        product = db.session.get(Product, item['product_id'])
        if product:
            cart_list.append(SimpleNamespace(product=product, quantity=item['quantity'], product_id=product.id))
    return cart_list


# --- Routes ---
@bp.route('/list')
def _list():
    cart_list = get_cart_items()
    stock_warnings = []

    for item in cart_list:
        product = item.product
        requested_qty = item.quantity

        if product.stock <= 0:
            stock_warnings.append(f"'{product.name}' 상품은 현재 품절되었습니다.")
        elif product.stock < requested_qty:
            stock_warnings.append(
                f"'{product.name}' 상품의 재고가 부족합니다. "
                f"(현재 재고: {product.stock}개 / 요청 수량: {requested_qty}개)"
            )

    product_total = sum(item.product.price * item.quantity for item in cart_list)

    shipping_fee = 3000
    if g.user and g.user.is_membership:
        shipping_fee = 0

    final_total = product_total + shipping_fee

    return render_template('order/cart_list.html',
                           cart_list=cart_list,
                           product_total=product_total,
                           shipping_fee=shipping_fee,
                           total_price=final_total,
                           stock_warnings=stock_warnings)


@bp.route('/add/<int:product_id>', methods=['GET', 'POST']) # POST 허용
def add(product_id):
    if g.user:
        cart = Cart.query.filter_by(user_id=g.user.id, product_id=product_id).first()
        if cart:
            cart.quantity += 1
        else:
            db.session.add(Cart(user_id=g.user.id, product_id=product_id, quantity=1))
        db.session.commit()
    else:
        guest_cart = get_guest_cart()
        item = next((i for i in guest_cart if i['product_id'] == product_id), None)
        if item:
            item['quantity'] += 1
        else:
            guest_cart.append({'product_id': product_id, 'quantity': 1})
        save_guest_cart(guest_cart)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # 최신 장바구니 데이터를 다시 조회
        if g.user:
            cart_items = Cart.query.filter_by(user_id=g.user.id).all()
        else:
            cart_items = get_guest_cart()  # 비회원 로직에 맞춰 수정

        return jsonify({
            'success': True,
            'cart_count': len(cart_items)  # 장바구니 아이템 개수 등 전달
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
    selected_ids = request.form.getlist('selected_ids', type=int)

    if not selected_ids:
        flash("삭제할 상품을 선택해주세요.")
        return redirect(url_for('order._list'))

    if g.user:
        Cart.query.filter(
            Cart.user_id == g.user.id,
            Cart.product_id.in_(selected_ids)
        ).delete(synchronize_session=False)
        db.session.commit()
    else:
        guest_cart = [i for i in get_guest_cart() if i['product_id'] not in selected_ids]
        save_guest_cart(guest_cart)

    flash(f"선택하신 {len(selected_ids)}개의 상품을 삭제했습니다.")
    return redirect(url_for('order._list'))


@bp.route('/modify/<int:product_id>/<string:action>', methods=['POST', 'GET'])
def modify(product_id, action):
    new_quantity = 0
    unit_price = 0
    is_deleted = False

    if g.user:
        cart_item = Cart.query.filter_by(user_id=g.user.id, product_id=product_id).first()
        if cart_item:
            # [핵심] 삭제되기 전에 상품 가격을 미리 변수에 저장합니다.
            unit_price = cart_item.product.price

            if action in ['inc', 'increase']:
                cart_item.quantity += 1
                new_quantity = cart_item.quantity
            elif action in ['dec', 'decrease']:
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    new_quantity = cart_item.quantity
                else:
                    # 여기서 삭제되므로, 이 이후에 cart_item을 사용하면 에러가 납니다.
                    db.session.delete(cart_item)
                    is_deleted = True
                    new_quantity = 0
            db.session.commit()
    else:
        # 비회원 로직
        guest_cart = get_guest_cart()
        new_guest_cart = []
        product = db.session.get(Product, product_id)
        unit_price = product.price if product else 0

        for item in guest_cart:
            if item['product_id'] == product_id:
                if action in ['inc', 'increase']:
                    item['quantity'] += 1
                    new_guest_cart.append(item)
                    new_quantity = item['quantity']
                elif action in ['dec', 'decrease']:
                    if item['quantity'] > 1:
                        item['quantity'] -= 1
                        new_guest_cart.append(item)
                        new_quantity = item['quantity']
                    else:
                        is_deleted = True
                        new_quantity = 0
            else:
                new_guest_cart.append(item)
        save_guest_cart(new_guest_cart)

    # 전체 금액 재계산
    cart_list = get_cart_items()
    pure_total = sum(item.product.price * item.quantity for item in cart_list)

    shipping_fee = 0
    if pure_total > 0:
        if g.user and getattr(g.user, 'is_membership', False):
            shipping_fee = 0
        else:
            shipping_fee = 3000

    final_total = pure_total + shipping_fee

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'new_quantity': new_quantity,
            'is_deleted': is_deleted,
            'item_total': format(unit_price * new_quantity, ','),
            'pure_total': format(pure_total, ','),  # 화면 표시용
            'total_price': format(final_total, ','),  # 화면 표시용
            'raw_pure_total': pure_total,  # ★ JS 계산용 숫자
            'raw_total_price': final_total  # ★ JS 계산용 숫자
        })

    return redirect(request.referrer or url_for('order._list'))


@bp.route('/delete/<int:product_id>')
def delete(product_id):
    if g.user:
        cart_item = Cart.query.filter_by(user_id=g.user.id, product_id=product_id).first()
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
    else:
        guest_cart = [i for i in get_guest_cart() if i['product_id'] != product_id]
        save_guest_cart(guest_cart)
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

    product_total = sum(item.product.price * item.quantity for item in cart_list)
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
    session['temp_recipient'] = data.get('recipient')
    session['temp_phone'] = data.get('phone')
    session['temp_address'] = data.get('address')
    session['applied_coupon_id'] = data.get('coupon_id')
    return jsonify({"success": True})


@bp.route('/success')
def success():
    payment_key = request.args.get('paymentKey')
    order_id = request.args.get('orderId')
    amount = request.args.get('amount')

    # 세션에서 쿠폰 ID 가져오기
    coupon_id = session.get('applied_coupon_id')

    # 토스페이먼츠 승인 API 호출 설정
    secret_key = "test_gsk_docs_OaPz8L5KdmQXkzRz3y47BMw6" + ":"
    encoded_key = base64.b64encode(secret_key.encode()).decode()
    url = "https://api.tosspayments.com/v1/payments/confirm"
    headers = {"Authorization": f"Basic {encoded_key}", "Content-Type": "application/json"}

    response = requests.post(url, json={
        "paymentKey": payment_key, "orderId": order_id, "amount": amount
    }, headers=headers)

    res_data = response.json()

    if response.status_code == 200:
        # 1. 쿠폰 할인액 재검증 및 사용 처리
        discount_amount = 0
        if coupon_id and g.user:
            coupon = Coupon.query.filter_by(id=coupon_id, user_id=g.user.id, is_used=False).first()
            if coupon:
                discount_amount = coupon.discount_amount
                coupon.is_used = True
                coupon.used_date = datetime.now()

        # 2. 주문 객체 생성 (UnboundLocalError 해결을 위해 바로 생성)
        order = Order(
            user_id=g.user.id if g.user else None,
            recipient=session.get('temp_recipient'),
            phone=session.get('temp_phone'),
            address=session.get('temp_address'),
            total_price=int(amount),
            payment_method=res_data.get('method', '카드/간편결제'),
            status='결제완료',
            coupon_id=coupon_id  # 모델에 컬럼이 있는 경우
        )

        db.session.add(order)
        db.session.commit()  # ID 생성을 위해 먼저 커밋

        # 3. 주문 아이템 생성 및 재고 차감
        # 주의: get_cart_items() 함수를 호출하여 리스트를 가져와야 합니다.
        cart_items = get_cart_items()
        for item in cart_items:
            order_item = OrderItem(
                order=order,
                product_id=item.product.id,
                quantity=item.quantity,
                price=item.product.price
            )
            db.session.add(order_item)

            # 재고 차감
            product = db.session.get(Product, item.product.id)
            if product:
                product.stock -= item.quantity

        # 4. 장바구니 비우기 및 세션 정리
        if g.user:
            Cart.query.filter_by(user_id=g.user.id).delete()
        else:
            session.pop('guest_cart', None)

        session.pop('applied_coupon_id', None)
        session.pop('temp_recipient', None)
        session.pop('temp_phone', None)
        session.pop('temp_address', None)

        db.session.commit()

        return render_template('order/order_complete.html', order=order, order_id=order.id)
    else:
        # 결제 실패 시 에러 메시지와 함께 리다이렉트
        flash(f"결제 승인 실패: {res_data.get('message')}")
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
            price=item.product.price
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

    if order.status == '결제완료':
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
        flash("이미 배송 중이거나 취소된 주문은 처리할 수 없습니다.")

    return redirect(url_for('order.order_detail', order_id=order_id))


@bp.route('/my_cancel_list')
@login_required
def my_cancel_list():
    three_months_ago = datetime.now() - timedelta(days=90)

    cancel_statuses = ['주문취소', '취소신청', '반품신청', '반품수거중', '반품완료']

    order_list = Order.query.filter(
        Order.user_id == g.user.id,
        Order.status.in_(cancel_statuses),
        Order.order_date >= three_months_ago
    ).order_by(Order.order_date.desc()).all()

    return render_template('order/mypage_cancel_list.html', order_list=order_list)


@bp.route('/confirm_purchase/<int:order_id>', methods=['POST'])
@login_required
def confirm_purchase(order_id):
    order = Order.query.get_or_404(order_id)

    if order.user_id != g.user.id:
        flash("잘못된 접근입니다.")
        return redirect(url_for('order.my_orders'))

    if order.status == '배송완료':
        order.status = '구매확정'
        db.session.commit()
        flash("구매가 확정되었습니다. 이제 리뷰를 작성하실 수 있습니다!")
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
    product_total = sum(item.product.price * item.quantity for item in cart_list)

    return dict(product_total=product_total)


# 파일 상단에 g, render_template 등이 임포트 되어있는지 확인하세요!
# (팀의 로그인 데코레이터 이름이 @login_required 라면 꼭 붙여주세요)

@bp.route('/wishlist')
@login_required  # 🌟 이 마법사를 달아주면 아래의 if문이 필요 없어집니다!
def wishlist():
    return render_template('order/wishlist.html')