from ConnectShop import create_app, db
from ConnectShop.models import User, MembershipBenefit, Coupon, Product, Cart, Order, OrderItem, Review, FAQ
# 🔥 비밀번호 암호화를 위한 도구 추가
from werkzeug.security import generate_password_hash
# db 삭제 후 재생성 시 오류 예방 코드
app = create_app()

with app.app_context():
    db.create_all()
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
    faq_data = [
        # ==========================================
        # 🚚 [배송 관련] (8개)
        # ==========================================
        ('배송', '배송은 얼마나 걸리나요?', '결제 완료 후 영업일 기준 1~3일 이내에 출고됩니다. (단, 도서산간 지역은 1~2일 추가 소요)'),
        ('배송', '주문/배송 상태는 어디에서 확인하나요?', '페이지 우측 상단의 사람 모양 아이콘 > [주문/배송조회]에서 확인 가능합니다. 비회원도 동일한 메뉴에서 조회할 수 있습니다.'),
        ('배송', '배송비를 알고 싶어요.', '기본 배송비는 3,000원입니다. 단, ConnectShop 멤버십 회원은 모든 상품이 100% 무료배송됩니다.'),
        ('배송', '주문 완료 후 배송지 변경이 가능한가요?', '상품 상태가 [결제완료] 또는 [상품준비중]일 때만 마이페이지에서 직접 수정 가능합니다. [배송중] 상태에서는 변경이 불가합니다.'),
        ('배송', '해외 배송도 가능한가요?', '죄송합니다. 현재 ConnectShop은 대한민국 내 배송만 지원하고 있습니다.'),
        ('배송', '방문 수령이나 퀵 배송도 가능한가요?',
         '고가의 전자기기 파손 위험을 방지하기 위해 지정된 공식 택배사를 통한 안전 배송만 진행하고 있으며, 방문 수령이나 오토바이 퀵 배송은 지원하지 않습니다.'),
        ('배송', '택배사는 어디를 이용하나요?',
         'ConnectShop은 안전하고 빠른 배송을 위해 우체국택배, CJ대한통운, 한진, 롯데, 로젠택배 등과 정식 제휴를 맺고 있습니다. (상품 크기에 따라 자동 배정)'),
        ('배송', '여러 상품을 주문했는데 묶음 배송이 가능한가요?',
         '동일한 일시에 결제된 주문건은 기본적으로 묶음 배송됩니다. 단, 물류센터 보관 위치가 다르거나 부피가 큰 데스크탑 등의 경우 개별 발송될 수 있습니다.'),

        # ==========================================
        # 🔄 [취소/교환/환불 관련] (9개)
        # ==========================================
        ('환불', '반품/환불 신청은 어떻게 하나요?', '상품 수령 후 7일 이내에 [마이페이지] > [주문내역]에서 반품 신청을 하실 수 있습니다.'),
        ('환불', '단순 변심으로 인한 교환/환불도 되나요?',
         '네, 가능합니다. 단, 단순 변심의 경우 왕복 배송비(6,000원)는 고객님께서 부담하셔야 하며, 제품 개봉이나 훼손 시에는 불가합니다.'),
        ('환불', '환불금은 언제 입금되나요?', '반품된 상품이 저희 물류센터에 도착하고 검수가 완료된 후, 영업일 기준 3~5일 이내에 결제하신 수단으로 취소/환불 처리됩니다.'),
        ('환불', '무통장 입금으로 결제했는데 환불은 어떻게 받나요?', '무통장 입금 고객님은 반품 신청 시 환불받으실 본인 명의의 계좌번호를 입력해 주시면 해당 계좌로 송금해 드립니다.'),
        ('환불', '여러 개를 샀는데 부분 취소/반품이 가능한가요?', '네, 가능합니다. 마이페이지 주문 내역에서 원하시는 상품만 선택하여 부분 취소 및 반품을 접수하실 수 있습니다.'),
        ('환불', '제품 불량으로 교환할 때 배송비는 어떻게 되나요?', '수령하신 제품이 초기 불량으로 판정될 경우, 교환/반품에 발생하는 모든 왕복 배송비는 ConnectShop이 전액 부담합니다.'),
        ('환불', '반품 주소지가 어떻게 되나요?', '반품 신청 시 제휴 택배사 기사님이 영업일 기준 1~2일 내로 고객님 댁으로 직접 방문 수거하므로 별도로 발송하실 필요가 없습니다.'),
        ('환불', '사은품이 포함된 상품을 반품하려면 어떻게 하나요?',
         '본 상품 반품 시 수령하신 사은품도 함께 동봉해 주셔야 정상적인 환불 처리가 가능합니다. 사은품 누락 시 환불이 지연될 수 있습니다.'),
        ('환불', '타 택배사를 이용해서 직접 반품해도 되나요?',
         '타 택배사 이용 시 배송 추적이 어렵고 분실 위험이 있어, 반드시 당사 마이페이지에서 제공하는 "반품/환불"기능을 이용해 주시기 바랍니다.'),

        # ==========================================
        # 💳 [주문/결제 관련] (9개)
        # ==========================================
        ('결제', '비회원도 구매할 수 있나요?', '네, 가능합니다. 장바구니에서 [비회원 구매하기]를 선택하시면 로그인 없이도 빠르고 간편하게 결제하실 수 있습니다.'),
        ('결제', '어떤 결제 수단을 지원하나요?', '현재 신용/체크카드, 네이버 페이, 퀵 계좌이체, 카카오페이, 페이코, 토스 등 다양한 결제 방식을 지원하고 있습니다.'),
        ('결제', '무통장 입금 기한은 언제까지인가요?', '주문 후 24시간 이내에 입금해 주셔야 하며, 기한 내 미입금 시 주문은 자동으로 취소됩니다.'),
        ('결제', '현금영수증 발급은 어떻게 하나요?', '무통장 입금 및 실시간 계좌이체 결제 시, 결제 화면에서 현금영수증(소득공제용/지출증빙용) 발급을 직접 신청하실 수 있습니다.'),
        ('결제', '결제 완료 후 결제 수단을 변경할 수 있나요?',
         '보안 및 결제망 시스템상 이미 완료된 결제의 수단 변경은 불가합니다. 기존 주문을 취소하시고 원하는 수단으로 재주문해 주시기 바랍니다.'),
        ('결제', '장바구니에 담은 상품은 언제까지 보관되나요?',
         '로그인한 회원의 장바구니 상품은 최대 30일간 보관되며, 비회원의 경우 브라우저 쿠키 삭제 전까지 보관됩니다. (단, 품절 시 자동 삭제)'),
        ('결제', '대량 구매(기업/학교) 시 할인이 가능한가요?',
         '기업, 공공기관, 학교 등에서 10대 이상 대량 구매를 원하시는 경우, 고객센터 1:1 문의를 이용하시면 담당 B2B 부서에서 특별 단가를 안내해 드립니다.'),
        ('결제', '주문을 취소했는데 카드사에서 승인 취소 문자가 안 와요.',
         'ConnectShop에서 취소 처리를 완료했더라도, 각 카드사의 매입/취소 처리 로직에 따라 실제 고객님께 문자가 가거나 한도가 복구되기까지 영업일 기준 3~5일이 소요될 수 있습니다.'),
        ('결제', '에스크로(안심결제) 서비스를 지원하나요?',
         '네, ConnectShop은 고객님의 안전한 거래를 위해 전자결제대행사(PG)를 통한 100% 에스크로(결제대금 예치) 서비스를 적용하고 있습니다.'),

        # ==========================================
        # 👤 [계정/회원 관련] (6개)
        # ==========================================
        ('계정', '비밀번호를 잊어버렸어요.', '로그인 화면 하단의 [아이디 찾기/비밀번호 재설정]을 클릭하신 후, 가입시 입력하신 이름과 이메일을 정확히 작성 후 비밀번호를 재설정해주시면 됩니다.'),
        ('계정', '회원 정보 수정은 어디서 하나요?', '로그인 후 [마이페이지] > [회원정보 수정] 메뉴에서 비밀번호를 변경하실 수 있습니다.'),
        ('계정', '회원 탈퇴는 어떻게 하나요?', '[마이페이지] 상단의 [정보수정] 옆쪽에 위치한 [회원 탈퇴] 버튼을 통해 진행하실 수 있습니다. 탈퇴 시 보유하신 쿠폰과 내역은 소멸됩니다.'),
        ('계정', '휴면 계정으로 전환되었다고 나오는데 어떻게 해제하나요?',
         '정보통신망법에 따라 1년 이상 미접속 시 휴면 계정으로 전환됩니다. 로그인 화면에서 아이디/비밀번호 입력 후 휴대폰 본인 인증을 거치면 즉시 해제됩니다.'),
        ('계정', 'SNS(카카오, 네이버) 계정으로도 가입할 수 있나요?', '현재 SNS 간편 로그인 연동 기능은 카카오를 이용한 가입만 제공해드리고 있습니다'),
        ('계정', '회원 탈퇴 후 재가입이 가능한가요?', '회원 탈퇴 후 부정 이용 방지를 위해 30일 동안은 동일한 이메일 및 연락처로 재가입이 제한됩니다.'),

        # ==========================================
        # 🎟️ [멤버십/쿠폰 관련] (5개)
        # ==========================================
        ('혜택', '멤버십 회원이 되면 어떤 혜택이 있나요?',
         'ConnectShop 멤버십 회원은 전 상품 무료 배송 혜택과 더불어, 커넥션케어(Connection Care) 가입 지원 등 프리미엄 혜택을 누리실 수 있습니다.'),
        ('혜택', '쿠폰은 어떻게 사용하나요?', '결제 화면의 [할인 및 쿠폰 적용] 란에서 보유하신 쿠폰을 선택하시면 총 결제 금액에서 즉시 차감됩니다.'),
        ('혜택', '발급받은 쿠폰의 유효기간이 지났어요.', '유효기간이 만료된 쿠폰은 자동으로 소멸되며 복구 및 연장이 불가능합니다. 기간 내 사용을 부탁드립니다.'),
        ('혜택', '비회원도 쿠폰을 받을 수 있나요?', '쿠폰 혜택은 회원 전용 서비스입니다. 회원가입을 하시면 신규 가입 축하 쿠폰을 즉시 발급해 드립니다.'),
        ('혜택', '한 주문에 여러 개의 쿠폰을 중복해서 사용할 수 있나요?', '기본적으로 상품 쿠폰과 장바구니 쿠폰은 1주문당 1개씩만 사용 가능합니다.'),
        # ==========================================
        # 💻 [A/S 및 제품 관련] (9개)
        # ==========================================
        ('A/S', '애플이나 삼성 제품의 공식 A/S가 가능한가요?',
         '네, ConnectShop에서 판매하는 모든 전자기기는 100% 정품이므로, 애플코리아 및 삼성전자 공식 서비스센터에서 정상적인 A/S를 받으실 수 있습니다.'),
        ('A/S', '제품 수리(A/S)를 ConnectShop에 맡길 수 있나요?',
         'ConnectShop은 판매처이므로 직접 수리를 진행하지 않습니다. 빠르고 정확한 처리를 위해 각 제조사의 공식 서비스센터를 이용해 주시기 바랍니다.'),
        ('A/S', '초기 불량인 것 같은데 어떻게 하나요?',
         '제품 수령 후 14일 이내에 제조사 공식 서비스센터를 방문하여 "불량 판정서"를 발급받아 고객센터로 문의해 주시면 즉시 새 제품 교환 또는 환불을 진행해 드립니다.'),
        ('A/S', '멤버십의 커넥션케어(Connection Care) 혜택은 무엇인가요?',
         '멤버십 회원에 한해 기기 구매 시 전 상품 배송비 무료를 지원해 드리며, 상품 관련 비용 할인 쿠폰이 지급됩니다.'),
        ('A/S', '전자기기 개봉 후에도 교환/환불이 되나요?',
         '전자기기 특성상 박스에 부착된 씰(Seal)을 훼손하거나 전원을 켠 이후에는 제품의 가치가 하락하므로, 명백한 기기 불량을 제외하고는 교환 및 환불이 절대 불가합니다.'),
        ('A/S', '판매하는 제품은 모두 정품인가요?', '네, ConnectShop은 각 브랜드의 공식 파트너 및 정식 총판을 통해서만 제품을 매입하므로 100% 확실한 정품임을 보장합니다.'),
        ('A/S', '품절된 상품의 재입고 일정은 어떻게 알 수 있나요?',
         '품절 상품 페이지에서 [재입고 알림 신청] 버튼을 누르시면, 해당 상품이 입고되는 즉시 카카오톡 알림톡이나 문자로 가장 먼저 안내해 드립니다.'),
        ('A/S', '전시 상품이나 중고/리퍼비시 제품도 판매하나요?', 'ConnectShop은 오직 미개봉 새 제품만 판매하고 있으며, 중고나 리퍼비시 제품은 취급하지 않습니다.'),
        ('A/S', '제품 구성품(케이블, 설명서 등)이 누락되어 도착했습니다.',
         '불편을 드려 죄송합니다. 수령일로부터 7일 이내에 고객센터 1:1 문의를 통해 문의주시면 제조사 확인 후 신속하게 누락된 부속품을 별도 발송해 드립니다.')
    ]

    # 객체 생성 및 DB 추가
    faq_objects = []
    for cat, ques, ans in faq_data:
        faq = FAQ(category=cat, question=ques, answer=ans)
        faq_objects.append(faq)

    db.session.add_all(faq_objects)

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
                   total_price=1799000, payment_method='무통장입금', status='배송중',courier_company='한진택배',tracking_number='536691845023')
    order2 = Order(user_id=u1.id, recipient='test01', phone='010-1234-5678', address='경기 성남시 분당구 판교역로 166',
                   total_price=1600000, payment_method='무통장입금', status='구매확정')
    order3 = Order(user_id=None, recipient='test01', phone='010-1234-5678', address='경기 성남시 분당구 판교역로 166',
                   total_price=1600000, payment_method='무통장입금', status='배송중',courier_company='CJ대한통운',tracking_number='511704834795')
    order4 = Order(user_id=u1.id, recipient='test01', phone='010-1234-5678', address='경기 성남시 분당구 판교역로 166',
                   total_price=1600000, payment_method='무통장입금', status='주문취소')
    order5 = Order(user_id=None, recipient='test01', phone='010-1234-5678', address='경기 성남시 분당구 판교역로 166',
                   total_price=1600000, payment_method='무통장입금', status='결제완료')
    db.session.add_all([order1, order2, order3, order4, order5])

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
    oi6 = OrderItem(order_id=order5.id, product_id=p1.id, quantity=1, price=1600000)

    db.session.add_all([oi1, oi2, oi3, oi4, oi5, oi6])

    # 🔥 최종 3차 커밋 (상세 내역 확정)
    db.session.commit()
    print("✅ 데이터베이스 대통합 완료!")