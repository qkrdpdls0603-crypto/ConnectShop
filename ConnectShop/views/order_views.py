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
    total_price = sum(item.product.price * item.quantity for item in cart_list)
    return render_template('order/cart_list.html', cart_list=cart_list, total_price=total_price)


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


@bp.route('/modify/<int:product_id>/<string:action>', methods=['POST', 'GET'])
def modify(product_id, action):
    new_quantity = 1
    unit_price = 0

    if g.user:
        cart_item = Cart.query.filter_by(user_id=g.user.id, product_id=product_id).first()
        if cart_item:
            if action in ['inc', 'increase']: cart_item.quantity += 1
            elif action in ['dec', 'decrease'] and cart_item.quantity > 1: cart_item.quantity -= 1
            db.session.commit()
            new_quantity = cart_item.quantity
            unit_price = cart_item.product.price
    else:
        guest_cart = get_guest_cart()
        for item in guest_cart:
            if item['product_id'] == product_id:
                if action in ['inc', 'increase']: item['quantity'] += 1
                elif action in ['dec', 'decrease'] and item['quantity'] > 1: item['quantity'] -= 1
                new_quantity = item['quantity']
                product = db.session.get(Product, product_id)
                unit_price = product.price if product else 0
                break
        save_guest_cart(guest_cart)

    # 전체 금액 계산
    cart_list = get_cart_items()
    total_price = sum(item.product.price * item.quantity for item in cart_list)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'new_quantity': new_quantity,
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

@bp.route('/checkout')
def checkout():
    cart_list = get_cart_items()

    if not cart_list:
        flash("장바구니가 비어 있습니다.")
        return redirect(url_for('order._list'))

    total_price = sum(item.product.price * item.quantity for item in cart_list)

    return render_template('order/checkout.html', cart_list=cart_list, total_price=total_price)


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

    total_price = sum(item.product.price * item.quantity for item in cart_list)

    new_order = Order(
        user_id=g.user.id if g.user else None,
        recipient=recipient,
        phone=phone,
        address=address,
        total_price=total_price,
        payment_method=payment_method
    )
    db.session.add(new_order)

    for item in cart_list:
        order_item = OrderItem(
            order=new_order,  # 위에서 만든 주문서와 연결
            product_id=item.product.id,
            quantity=item.quantity,
            price=item.product.price  # 주문 시점의 가격 기록
        )
        db.session.add(order_item)

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

    return render_template('order/order_detail.html', order=order)

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
        order.status = '주문취소'
        db.session.commit()
        flash(f"주문 #{order_id}번 건이 정상적으로 취소되었습니다.")
    else:
        flash("이미 배송 중이거나 취소된 주문은 처리할 수 없습니다.")

    return redirect(request.referrer or url_for('main.index'))


@bp.route('/my_cancel_list')
@login_required
def my_cancel_list():
    cancel_statuses = ['주문취소', '취소신청', '반품신청', '반품수거중', '반품완료']

    cancel_orders = Order.query.filter(
        Order.user_id == g.user.id,
        Order.status.in_(cancel_statuses)
    ).order_by(Order.order_date.desc()).all()

    return render_template('order/mypage_cancel_list.html', order_list=cancel_orders)


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

