import base64
import requests

from datetime import timedelta, datetime
from types import SimpleNamespace
from flask import Blueprint, render_template, redirect, url_for, session, g, flash, jsonify, request

from ConnectShop import db
from ConnectShop.models import Cart, Product, Order, OrderItem
from ConnectShop.views.auth_views import login_required

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


@bp.route('/add/<int:product_id>')
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
    total_price = sum(item.product.price * item.quantity for item in cart_list)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'new_quantity': new_quantity,
            'is_deleted': is_deleted,
            'item_total': format(unit_price * new_quantity, ','),
            'total_price': format(total_price, ',')
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
    if request.method == 'POST':
        # 사용자가 입력한 정보를 세션에 임시 저장
        session['temp_order_info'] = {
            'recipient': request.form.get('recipient'),
            'phone': request.form.get('phone'),
            'address': f"{request.form.get('address')} {request.form.get('address_detail')}"
        }

    cart_list = get_cart_items()

    if not cart_list:
        flash("장바구니가 비어 있습니다.")
        return redirect(url_for('order._list'))

    for item in cart_list:
        if item.product.stock < item.quantity:
            flash(f"상품 '{item.product.name}'의 재고가 부족합니다. (현재 재고: {item.product.stock}개)")
            return redirect(url_for('cart.view_cart'))

    now_ts = datetime.now().strftime('%Y%m%d%H%M%S')

    product_total = sum(item.product.price * item.quantity for item in cart_list)
    shipping_fee = 0 if (g.user and g.user.is_membership) else 3000
    final_total = product_total + shipping_fee

    return render_template('order/checkout.html',
                           cart_list=cart_list,
                           total_price=final_total,  # 배송비가 포함된 금액을 넘겨줌
                           now_ts=now_ts)

@bp.route('/save_temp_info', methods=['POST'])
def save_temp_info():
    data = request.get_json()
    session['temp_recipient'] = data.get('recipient')
    session['temp_phone'] = data.get('phone')
    session['temp_address'] = data.get('address')
    return jsonify({"success": True})


@bp.route('/success')
def success():
    payment_key = request.args.get('paymentKey')
    order_id = request.args.get('orderId')
    amount = request.args.get('amount')

    secret_key = "test_gsk_docs_OaPz8L5KdmQXkzRz3y47BMw6" + ":"
    encoded_key = base64.b64encode(secret_key.encode()).decode()
    url = "https://api.tosspayments.com/v1/payments/confirm"
    headers = {"Authorization": f"Basic {encoded_key}", "Content-Type": "application/json"}

    response = requests.post(url, json={
        "paymentKey": payment_key, "orderId": order_id, "amount": amount
    }, headers=headers)

    res_data = response.json()

    if response.status_code == 200:
        from ConnectShop.models import Order, OrderItem, Product, Cart

        clean_id = order_id.replace("order_temp_", "") if "order_temp_" in order_id else order_id
        order = Order.query.get(clean_id) if clean_id.isdigit() else None

        if not order:
            cart_list = get_cart_items()
            method = res_data.get('method', '카드/간편결제')

            # 세션에서 진짜 사용자가 입력한 정보를 꺼내옵니다.
            # 만약 세션에도 없다면 그때만 기본값을 넣습니다.
            order = Order(
                user_id=g.user.id if g.user else None,
                recipient=session.get('temp_recipient'),
                phone=session.get('temp_phone'),
                address=session.get('temp_address'),
                total_price=int(amount),
                payment_method=method,
                status='결제완료'
            )
            db.session.add(order)
            db.session.commit()  # 여기서 실제 DB에 저장됨

            for item in cart_list:
                order_item = OrderItem(order=order, product_id=item.product.id, quantity=item.quantity,
                                       price=item.product.price)
                db.session.add(order_item)
                product = Product.query.get(item.product.id)
                if product: product.stock -= item.quantity

            if g.user:
                Cart.query.filter_by(user_id=g.user.id).delete()
            else:
                session.pop('guest_cart', None)

            db.session.commit()

        return render_template('order/order_complete.html', order=order, order_id=order.id)
    else:
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


@bp.route('/refund/<int:order_id>/<int:item_id>/<string:type>')
def refund_request(order_id, item_id, type):
    order = Order.query.get_or_404(order_id)

    flash(f"주문 #{order_id}번 상품의 {type} 신청이 접수되었습니다. (로직 구현 필요)")
    return redirect(url_for('order.order_detail', order_id=order_id))