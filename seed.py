from ConnectShop import create_app, db
from ConnectShop.models import User, MembershipBenefit, Coupon, Product, Cart, Order, OrderItem, Review, FAQ
# 🔥 비밀번호 암호화를 위한 도구 추가
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # --- [주의] 삭제할 때는 생성의 '역순'으로 지워야 에러가 안 납니다! ---
    print("🧹 기존 데이터를 초기화합니다...")
    OrderItem.query.delete()
    Review.query.delete()
    Order.query.delete()
    Cart.query.delete()
    Coupon.query.delete()
    MembershipBenefit.query.delete()
    Product.query.delete()
    User.query.delete()
    FAQ.query.delete()
    db.session.commit()

    print("🚀 새로운 통합 데이터를 쏟아붓습니다!")

    # ==========================================
    # Phase 1. 부모 데이터 생성 (User, Product, FAQ)
    # ==========================================
    print("👥 회원, 상품, FAQ 데이터를 생성하는 중...")

    # [팀원 1] User 생성 (암호화 적용)
    u1 = User(
        username='박예인',
        password=generate_password_hash('1234'),
        email='qkrdpdls0603@gmail.com',
        phone='01091324245'
    )

    # [팀원 4 - 이강토] User 생성 (암호화 적용)
    u2 = User(
        username='이강토',
        password=generate_password_hash('1234'),
        email='gangto@gmail.com',
        phone='01085253445'
    )

    db.session.add_all([u1, u2])

    # [팀원 2] User 데이터 생성 (총 25명, 반복문 내 암호화 적용)
    membership_targets = ['test', 'test1', 'test2', 'test3', 'test4']
    raw_users = [
        ('test', 'test01@test.com', '01012341234'), ('test1', 'test02@test.com', '01012341235'),
        ('test2', 'test03@test.com', '01012341236'), ('test3', 'test04@test.com', '01012341237'),
        ('test4', 'test05@test.com', '01012341238'), ('test5', 'test06@test.com', '01012341239'),
        ('test6', 'test07@test.com', '01012341230'), ('test7', 'test08@test.com', '01012341240'),
        ('test8', 'test09@test.com', '01012341241'), ('test9', 'test10@test.com', '01012341242'),
        ('test10', 'test11@test.com', '01012341243'), ('test11', 'test12@test.com', '01012341244'),
        ('test12', 'test13@test.com', '01012341245'), ('test13', 'test14@test.com', '01012341246'),
        ('test14', 'test15@test.com', '01012341247'), ('test15', 'test16@test.com', '01012341248'),
        ('test00', 'test@test.com', '01011111111'), ('test30', 'test30@test.com', '01011111112'),
        ('test31', 'test31@test.com', '01011111113'), ('test33', 'test33@test.com', '01011111114'),
        ('test34', 'test34@test.com', '01011111115'), ('test36', 'test36@test.com', '01011112222'),
        ('test37', 'test37@test.com', '01011112223'), ('test40', 'test40@test.com', '01011112323'),
        ('test41', 'test41@test.com', '01011114444')
    ]

    user_objects = {}
    # 공통 임시 비밀번호 해시 생성 (반복문 밖에서 한 번만 생성하여 속도 최적화)
    common_password_hash = generate_password_hash('1234')

    for username, email, phone in raw_users:
        is_mem = True if username in membership_targets else False
        user = User(
            username=username,
            password=common_password_hash,
            email=email,
            phone=phone,
            is_membership=is_mem
        )
        db.session.add(user)
        user_objects[username] = user

    # [팀원 1] Product 생성
    p1 = Product(name='갤럭시 S26 울트라', price=1600000, category='스마트폰', brand='삼성', stock=10, description='테스트용 상품 1',
                 image_path='phone1.jpg')
    p2 = Product(name='애플 에어팟', price=199000, category='무선이어폰', brand='애플', stock=20, description='테스트용 상품 2',
                 image_path='ear2.jpg')
    p3 = Product(name='소니 WH 헤드폰', price=459000, category='헤드폰', brand='소니', stock=15, description='테스트용 상품 3',
                 image_path='headphone1.jpg')
    p4 = Product(name='맥북 에어 M3', price=1590000, category='노트북', brand='애플', stock=5, description='테스트용 상품 4',
                 image_path='notebook2.jpg')
    p5 = Product(name='갤럭시 워치 8', price=350000, category='스마트워치', brand='삼성', stock=30, description='테스트용 상품 5',
                 image_path='watch1.jpg')
    db.session.add_all([p1, p2, p3, p4, p5])

    # [팀원 4 - 이강토] FAQ 생성
    faq1 = FAQ(category='배송', question='배송은 얼마나 걸리나요?', answer='결제 완료 후 영업일 기준 1~3일 이내에 출고됩니다.')
    faq2 = FAQ(category='환불', question='반품 신청은 어떻게 하나요?', answer='마이페이지 > 주문내역에서 수령 후 7일 이내에 신청 가능합니다.')
    faq3 = FAQ(category='계정', question='비밀번호를 잊어버렸어요.', answer='로그인 화면 하단의 [비밀번호 찾기]를 이용해 주세요.')
    faq4 = FAQ(category='배송', question='주문/배송 상태는 어디에서 확인하나요?',
               answer='주문/배송 상태는 페이지 우측 상단의 사람 모양 아이콘에서 주문/배송조회에서 확인할 수 있습니다.<br>비회원 주문/배송조회도 우측 상단의 사람 모양 아이콘에서 이용하실 수 있습니다.')
    db.session.add_all([faq1, faq2, faq3, faq4])

    # 🔥 1차 커밋 (모든 회원, 상품, FAQ의 ID 번호가 발급됩니다)
    db.session.commit()

    # ==========================================
    # Phase 2. 1차 자식 데이터 생성 (Membership, Coupon, Cart, Order)
    # ==========================================
    print("🎫 혜택 및 주문(영수증) 데이터를 생성하는 중...")

    # [팀원 2] MembershipBenefit 생성
    for username in membership_targets:
        benefit = MembershipBenefit(user_id=user_objects[username].id, has_apple_care=True, free_shipping=True)
        db.session.add(benefit)

    # [팀원 2] Coupon 생성
    for username, user_obj in user_objects.items():
        if username in membership_targets:
            db.session.add(Coupon(user_id=user_obj.id, discount_amount=1000))
            db.session.add(Coupon(user_id=user_obj.id, discount_amount=3000))
        else:
            db.session.add(Coupon(user_id=user_obj.id, discount_amount=1000))

    # [팀원 1] Order 생성
    order1 = Order(user_id=u1.id, recipient='test01', phone='010-1234-5678', address='경기 성남시 분당구 판교역로 166',
                   total_price=1799000, payment_method='transfer', status='배송중')
    order2 = Order(user_id=u1.id, recipient='test01', phone='010-1234-5678', address='경기 성남시 분당구 판교역로 166',
                   total_price=1600000, payment_method='무통장입금', status='구매확정')
    order3 = Order(user_id=None, recipient='test01', phone='010-1234-5678', address='경기 성남시 분당구 판교역로 166',
                   total_price=1600000, payment_method='무통장입금', status='결제완료')
    order4 = Order(user_id=u1.id, recipient='test01', phone='010-1234-5678', address='경기 성남시 분당구 판교역로 166',
                   total_price=1600000, payment_method='무통장입금', status='주문취소')
    db.session.add_all([order1, order2, order3, order4])

    # 🔥 2차 커밋 (멤버십, 쿠폰, 그리고 영수증 번호가 발급됩니다)
    db.session.commit()

    # ==========================================
    # Phase 3. 2차 자식 데이터 생성 (OrderItem, Review)
    # ==========================================
    print("🛒 주문 상세 내역을 엮는 중...")

    # [팀원 1] OrderItem 생성
    oi1 = OrderItem(order_id=order1.id, product_id=p1.id, quantity=1, price=1600000)
    oi2 = OrderItem(order_id=order1.id, product_id=p2.id, quantity=1, price=199000)
    oi3 = OrderItem(order_id=order2.id, product_id=p1.id, quantity=1, price=1600000)
    oi4 = OrderItem(order_id=order3.id, product_id=p1.id, quantity=1, price=1600000)
    oi5 = OrderItem(order_id=order4.id, product_id=p1.id, quantity=1, price=1600000)

    db.session.add_all([oi1, oi2, oi3, oi4, oi5])

    # 🔥 최종 3차 커밋 (상세 내역 확정)
    db.session.commit()
    print("✅ 데이터베이스 대통합 완료!")