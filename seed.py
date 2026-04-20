import random
from datetime import datetime, timedelta
from ConnectShop import create_app, db
from ConnectShop.models import User, MembershipBenefit, Coupon, Product, Cart, Order, OrderItem, Review, FAQ, ProductOption
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
    ProductOption.query.delete()
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

    # -------------------------------------------------------------------
    # 1. 대표 상품 5개 (p1~p5 : 옵션이나 타 기능에서 참조하기 위해 변수로 고정)
    # -------------------------------------------------------------------
    p1 = Product(name='갤럭시 S26 울트라', price=1690000, category='스마트폰', brand='삼성', stock=10,

                 description='가장 완벽한 AI 스마트폰', image_path='phone_sam1.jpg', box_image_path='images/sam1_box.jpg',

                 box_description='스마트폰 | 데이터 케이블 | 분리핀')
    p2 = Product(name='애플 에어팟', price=199000, category='무선이어폰', brand='애플', stock=20, description='테스트용 상품 2',
                 image_path='ear2.jpg')
    p3 = Product(name='소니 WH 헤드폰', price=459000, category='헤드폰', brand='소니', stock=15, description='테스트용 상품 3',
                 image_path='headphone1.jpg')
    p4 = Product(name='맥북 에어 M3', price=1590000, category='노트북', brand='애플', stock=5, description='테스트용 상품 4',
                 image_path='notebook2.jpg')
    p5 = Product(name='갤럭시 워치 8', price=350000, category='스마트워치', brand='삼성', stock=30, description='테스트용 상품 5',
                 image_path='watch1.jpg', box_image_path='images/watch1_box_all.avif',
                 box_description='1. 갤럭시 워치8 | 2. 무선 충전기 | 3. 간단 사용 설명서<br>※ 구성 요소는 국가 및 컬러에 따라 다를 수 있습니다.')

    # -------------------------------------------------------------------
    # 2. 나머지 대량의 스마트폰 라인업 (39개)
    # -------------------------------------------------------------------
    other_smartphones = [
        # --- 삼성 (Samsung) 추가 7개 ---
        Product(name='갤럭시 S26+', price=1350000, category='스마트폰', brand='삼성', stock=15,
                description='더 커진 화면, 압도적 성능', image_path='phone_sam2.jpg'),
        Product(name='갤럭시 S26', price=1150000, category='스마트폰', brand='삼성', stock=20,
                description='한 손에 쏙 들어오는 컴팩트 플래그십', image_path='phone_sam3.jpg'),
        Product(name='갤럭시 Z 폴드 6', price=2100000, category='스마트폰', brand='삼성', stock=5,
                description='대화면의 혁신, 접는 스마트폰의 완성', image_path='phone_sam4.jpg'),
        Product(name='갤럭시 Z 플립 6', price=1390000, category='스마트폰', brand='삼성', stock=12,
                description='트렌디한 디자인, 완벽한 포켓 사이즈', image_path='phone_sam5.jpg'),
        Product(name='갤럭시 S24 FE', price=840000, category='스마트폰', brand='삼성', stock=25,
                description='플래그십 경험을 합리적인 가격에', image_path='phone_sam6.jpg'),
        Product(name='갤럭시 A55', price=550000, category='스마트폰', brand='삼성', stock=30, description='가성비 끝판왕 미들레인지',
                image_path='phone_sam7.jpg'),
        Product(name='갤럭시 A35', price=450000, category='스마트폰', brand='삼성', stock=40,
                description='실용성을 극대화한 보급형 스마트폰', image_path='phone_sam8.jpg'),

        # --- 애플 (Apple) 8개 ---
        Product(name='아이폰 17 프로 맥스', price=1900000, category='스마트폰', brand='애플', stock=8,
                description='티타늄 디자인과 최고의 배터리', image_path='phone_app1.jpg'),
        Product(name='아이폰 17 프로', price=1550000, category='스마트폰', brand='애플', stock=15,
                description='강력한 A18 Pro 칩셋 탑재', image_path='phone_app2.jpg'),
        Product(name='아이폰 17 에어', price=1350000, category='스마트폰', brand='애플', stock=10,
                description='역대 가장 슬림한 디자인, 상상을 뛰어넘는 가벼움', image_path='phone_app3.jpg'),
        Product(name='아이폰 17', price=1250000, category='스마트폰', brand='애플', stock=20, description='새로운 듀얼 카메라 시스템',
                image_path='phone_app4.jpg'),
        Product(name='아이폰 16 프로', price=1450000, category='스마트폰', brand='애플', stock=12,
                description='여전히 강력한 성능의 프로', image_path='phone_app5.jpg'),
        Product(name='아이폰 16', price=1150000, category='스마트폰', brand='애플', stock=18, description='모두를 위한 완벽한 기본기',
                image_path='phone_app6.jpg'),
        Product(name='아이폰 SE (4세대)', price=650000, category='스마트폰', brand='애플', stock=35,
                description='홈 버튼의 귀환, 클래식과 모던의 조화', image_path='phone_app7.jpg'),
        Product(name='아이폰 15', price=950000, category='스마트폰', brand='애플', stock=22, description='입문용으로 완벽한 선택',
                image_path='phone_app8.jpg'),

        # --- 샤오미 (Xiaomi) 8개 ---
        Product(name='샤오미 14 울트라', price=1300000, category='스마트폰', brand='샤오미', stock=5,
                description='라이카 협업, 카메라의 신세계', image_path='phone_xia1.jpg'),
        Product(name='샤오미 14 프로', price=1050000, category='스마트폰', brand='샤오미', stock=10, description='플래그십 성능의 표준',
                image_path='phone_xia2.jpg'),
        Product(name='샤오미 14', price=850000, category='스마트폰', brand='샤오미', stock=15,
                description='컴팩트한 크기에 담긴 괴물 성능', image_path='phone_xia3.jpg'),
        Product(name='레드미 노트 13 프로+ 5G', price=550000, category='스마트폰', brand='샤오미', stock=25,
                description='2억 화소 카메라 탑재 가성비폰', image_path='phone_xia4.jpg'),
        Product(name='레드미 노트 13 프로', price=400000, category='스마트폰', brand='샤오미', stock=30,
                description='학생용, 업무용 1티어', image_path='phone_xia5.jpg'),
        Product(name='레드미 노트 13', price=290000, category='스마트폰', brand='샤오미', stock=40,
                description='부담 없는 갓성비 스마트폰', image_path='phone_xia6.jpg'),
        Product(name='포코 F6 프로', price=600000, category='스마트폰', brand='샤오미', stock=20, description='게이밍에 특화된 퍼포먼스',
                image_path='phone_xia7.jpg'),
        Product(name='포코 X6 프로', price=450000, category='스마트폰', brand='샤오미', stock=25, description='타협 없는 성능과 가격',
                image_path='phone_xia8.jpg'),

        # --- 구글 (Google) 8개 ---
        Product(name='구글 픽셀 9 프로 폴드', price=1950000, category='스마트폰', brand='구글', stock=3,
                description='구글의 첫 번째 초슬림 폴더블', image_path='phone_goo1.JPEG'),
        Product(name='구글 픽셀 9 프로 XL', price=1450000, category='스마트폰', brand='구글', stock=8,
                description='극대화된 화면과 구글 AI', image_path='phone_goo2.JPEG'),
        Product(name='구글 픽셀 9 프로', price=1300000, category='스마트폰', brand='구글', stock=10,
                description='순정 안드로이드의 끝판왕', image_path='phone_goo3.JPEG'),
        Product(name='구글 픽셀 9', price=1050000, category='스마트폰', brand='구글', stock=15, description='더 똑똑해진 일상 AI 비서',
                image_path='phone_goo4.JPEG'),
        Product(name='구글 픽셀 8a', price=650000, category='스마트폰', brand='구글', stock=20, description='픽셀의 경험을 가장 저렴하게',
                image_path='phone_goo5.JPEG'),
        Product(name='구글 픽셀 8 프로', price=1100000, category='스마트폰', brand='구글', stock=7,
                description='여전히 훌륭한 전세대 플래그십', image_path='phone_goo6.JPEG'),
        Product(name='구글 픽셀 8', price=850000, category='스마트폰', brand='구글', stock=12, description='가장 균형 잡힌 구글폰',
                image_path='phone_goo7.JPEG'),
        Product(name='구글 픽셀 7a', price=450000, category='스마트폰', brand='구글', stock=18,
                description='부담 없이 즐기는 안드로이드 레퍼런스', image_path='phone_goo8.JPEG'),

        # --- 모토로라 (Motorola) 8개 ---
        Product(name='모토로라 엣지 50 울트라', price=1200000, category='스마트폰', brand='모토로라', stock=5,
                description='원목 재질 마감의 독보적 디자인', image_path='phone_mot1.JPEG'),
        Product(name='모토로라 엣지 50 프로', price=850000, category='스마트폰', brand='모토로라', stock=10,
                description='아름다운 곡면 디스플레이', image_path='phone_mot2.JPEG'),
        Product(name='모토로라 엣지 50 퓨전', price=550000, category='스마트폰', brand='모토로라', stock=15,
                description='스타일리시 미들레인지', image_path='phone_mot3.JPEG'),
        Product(name='모토로라 레이저 50 울트라', price=1350000, category='스마트폰', brand='모토로라', stock=8,
                description='가장 넓은 외부 디스플레이 폴더블', image_path='phone_mot4.JPEG'),
        Product(name='모토로라 레이저 50', price=990000, category='스마트폰', brand='모토로라', stock=12,
                description='대중화를 선언한 폴더블폰', image_path='phone_mot5.JPEG'),
        Product(name='모토 g84 5G', price=400000, category='스마트폰', brand='모토로라', stock=25,
                description='비건 레더 마감의 가성비 5G', image_path='phone_mot6.JPEG'),
        Product(name='모토 g54', price=300000, category='스마트폰', brand='모토로라', stock=30, description='엔터테인먼트에 특화된 보급형',
                image_path='phone_mot7.JPEG'),
        Product(name='모토 g34', price=200000, category='스마트폰', brand='모토로라', stock=40, description='세컨폰으로 완벽한 초가성비',
                image_path='phone_mot8.JPEG'),
    ]

    # -------------------------------------------------------------------
    # 2-2. 대량의 무선이어폰 라인업 (40개)
    # -------------------------------------------------------------------
    other_earphones = [
        # --- 삼성 (Samsung) 8개 ---
        Product(name='갤럭시 버즈3 프로', price=319000, category='무선이어폰', brand='삼성', stock=20,
                description='궁극의 몰입감을 선사하는 프로 사운드', image_path='ear_sam1.JPEG'),
        Product(name='갤럭시 버즈3', price=219000, category='무선이어폰', brand='삼성', stock=25,
                description='편안한 오픈형 디자인의 완벽한 진화', image_path='ear_sam2.JPEG'),
        Product(name='갤럭시 버즈2 프로', price=279000, category='무선이어폰', brand='삼성', stock=15,
                description='24bit Hi-Fi 사운드의 감동', image_path='ear_sam3.JPEG'),
        Product(name='갤럭시 버즈 FE', price=119000, category='무선이어폰', brand='삼성', stock=40,
                description='핵심 기능만 담은 가성비 버즈', image_path='ear_sam4.jpg'),
        Product(name='갤럭시 버즈2', price=149000, category='무선이어폰', brand='삼성', stock=30, description='가볍고 편안한 데일리 이어폰',
                image_path='ear_sam5.JPEG'),
        Product(name='갤럭시 버즈 라이브', price=139000, category='무선이어폰', brand='삼성', stock=10,
                description='유니크한 강낭콩 디자인의 오픈형', image_path='ear_sam6.JPEG'),
        Product(name='갤럭시 버즈 프로', price=199000, category='무선이어폰', brand='삼성', stock=5,
                description='삼성의 첫 프리미엄 ANC 이어폰', image_path='ear_sam7.JPEG'),
        Product(name='갤럭시 버즈+', price=99000, category='무선이어폰', brand='삼성', stock=8, description='압도적인 배터리 타임의 전설',
                image_path='ear_sam8.jpg'),

        # --- 애플 (Apple) 8개 (Beats 포함) ---
        Product(name='에어팟 프로 (2세대, USB-C)', price=359000, category='무선이어폰', brand='애플', stock=30,
                description='최대 2배 강력해진 노이즈 캔슬링', image_path='ear_app1.jpg'),
        Product(name='에어팟 (3세대, MagSafe)', price=269000, category='무선이어폰', brand='애플', stock=25,
                description='공간 음향으로 입체감 넘치는 사운드', image_path='ear_app2.jpg'),
        Product(name='에어팟 (3세대, Lightning)', price=259000, category='무선이어폰', brand='애플', stock=15,
                description='에어팟 3세대를 조금 더 합리적으로', image_path='ear_app3.jpg'),
        Product(name='에어팟 (2세대)', price=199000, category='무선이어폰', brand='애플', stock=40,
                description='무선 이어폰의 시대를 연 클래식', image_path='ear_app4.jpg'),
        Product(name='에어팟 프로 (1세대)', price=250000, category='무선이어폰', brand='애플', stock=5,
                description='애플 ANC의 훌륭한 시작점', image_path='ear_app5.jpg'),
        Product(name='Beats Studio Buds+', price=229000, category='무선이어폰', brand='애플', stock=20,
                description='투명한 디자인과 향상된 노이즈 캔슬링', image_path='ear_app6.jpg'),
        Product(name='Beats Fit Pro', price=269000, category='무선이어폰', brand='애플', stock=12,
                description='안정적인 윙팁, 운동에 최적화된 핏', image_path='ear_app7.jpg'),
        Product(name='Powerbeats Pro', price=269000, category='무선이어폰', brand='애플', stock=8,
                description='단단하게 귀를 감싸는 이어훅 디자인', image_path='ear_app8.JPEG'),

        # --- 샤오미 (Xiaomi) 8개 ---
        Product(name='레드미 버즈 5 프로', price=79000, category='무선이어폰', brand='샤오미', stock=35,
                description='하이 레졸루션 오디오 인증, 동급 최강 ANC', image_path='ear_xia1.JPEG'),
        Product(name='레드미 버즈 5', price=49000, category='무선이어폰', brand='샤오미', stock=50,
                description='가성비 ANC 무선 이어폰의 새로운 기준', image_path='ear_xia2.JPEG'),
        Product(name='샤오미 버즈 4 프로', price=189000, category='무선이어폰', brand='샤오미', stock=15,
                description='샤오미 프리미엄 사운드의 결정체', image_path='ear_xia3.jpg'),
        Product(name='레드미 버즈 4 액티브', price=25000, category='무선이어폰', brand='샤오미', stock=60,
                description='놀라운 가격, 탄탄한 기본기', image_path='ear_xia4.jpg'),
        Product(name='레드미 버즈 4 라이트', price=29000, category='무선이어폰', brand='샤오미', stock=45,
                description='깃털처럼 가벼운 하프 인이어', image_path='ear_xia5.jpg'),
        Product(name='레드미 버즈 4 프로', price=89000, category='무선이어폰', brand='샤오미', stock=20,
                description='듀얼 다이내믹 드라이버 탑재', image_path='ear_xia6.JPEG'),
        Product(name='샤오미 버즈 3T 프로', price=139000, category='무선이어폰', brand='샤오미', stock=10,
                description='고급스러운 무광 디자인과 입체 음향', image_path='ear_xia7.JPEG'),
        Product(name='샤오미 버즈 3', price=99000, category='무선이어폰', brand='샤오미', stock=12,
                description='안정적인 연결, 깨끗한 통화 품질', image_path='ear_xia8.jpg'),

        # --- 샥즈 (Shokz) 8개 ---
        Product(name='오픈핏 (OpenFit)', price=249000, category='무선이어폰', brand='샥즈', stock=20,
                description='완전 무선 공기전도 이어폰의 혁신', image_path='ear_shokz1.JPEG'),
        Product(name='오픈핏 에어 (OpenFit Air)', price=175000, category='무선이어폰', brand='샥즈', stock=25,
                description='더 가볍고 합리적인 오픈핏', image_path='ear_shokz2.JPEG'),
        Product(name='오픈런 프로 (OpenRun Pro)', price=239000, category='무선이어폰', brand='샥즈', stock=15,
                description='저음역대가 강화된 프리미엄 골전도', image_path='ear_shokz3.JPEG'),
        Product(name='오픈런 (OpenRun)', price=175000, category='무선이어폰', brand='샥즈', stock=30,
                description='가장 사랑받는 베스트셀러 골전도 이어폰', image_path='ear_shokz4.JPEG'),
        Product(name='오픈스윔 프로 (OpenSwim Pro)', price=249000, category='무선이어폰', brand='샥즈', stock=10,
                description='수영부터 러닝까지, 블루투스와 MP3 동시지원', image_path='ear_shokz5.JPEG'),
        Product(name='오픈스윔 (OpenSwim)', price=199000, category='무선이어폰', brand='샥즈', stock=8,
                description='수중 음악 감상을 위한 MP3 골전도 이어폰', image_path='ear_shokz6.JPEG'),
        Product(name='오픈무브 (OpenMove)', price=119000, category='무선이어폰', brand='샥즈', stock=35,
                description='골전도 이어폰 입문용으로 최고의 선택', image_path='ear_shokz7.JPEG'),
        Product(name='오픈컴 2 (OpenComm 2)', price=214000, category='무선이어폰', brand='샥즈', stock=12,
                description='비즈니스 통화에 최적화된 붐 마이크 탑재', image_path='ear_shokz8.JPEG'),

        # --- 소니 (Sony) 8개 ---
        Product(name='WF-1000XM5', price=359000, category='무선이어폰', brand='소니', stock=25,
                description='한 차원 진화한 헤드폰급 노이즈 캔슬링', image_path='ear_sony1.JPEG'),
        Product(name='WF-1000XM4', price=259000, category='무선이어폰', brand='소니', stock=10,
                description='여전히 훌륭한 소니의 명기', image_path='ear_sony2.JPEG'),
        Product(name='LinkBuds S', price=249000, category='무선이어폰', brand='소니', stock=20,
                description='세상에서 가장 작고 가벼운 고음질 노캔 이어폰', image_path='ear_sony3.JPEG'),
        Product(name='LinkBuds', price=229000, category='무선이어폰', brand='소니', stock=15,
                description='벗지 않는 편안함, 링 디자인 오픈형', image_path='ear_sony4.JPEG'),
        Product(name='WF-C700N', price=149000, category='무선이어폰', brand='소니', stock=30,
                description='가볍게 즐기는 소니의 노이즈 캔슬링', image_path='ear_sony5.JPEG'),
        Product(name='WF-C500', price=99000, category='무선이어폰', brand='소니', stock=40,
                description='컴팩트한 디자인의 소니 입문용 모델', image_path='ear_sony6.JPEG'),
        Product(name='WF-SP800N', price=169000, category='무선이어폰', brand='소니', stock=5,
                description='강력한 베이스와 방수를 지원하는 스포츠용', image_path='ear_sony7.JPEG'),
        Product(name='WF-XB700', price=119000, category='무선이어폰', brand='소니', stock=8,
                description='심장을 울리는 EXTRA BASS 사운드', image_path='ear_sony8.JPEG'),
    ]

    # -------------------------------------------------------------------
    # 2-3. 대량의 스마트워치 라인업 (39개 - 기존 p5 제외)
    # -------------------------------------------------------------------
    other_smartwatches = [
        # --- 삼성 (Samsung) 7개 (기존 p5 포함 총 8개) ---
        Product(name='갤럭시 워치7', price=329000, category='스마트워치', brand='삼성', stock=20,
                description='더욱 강력해진 헬스케어 파트너', image_path='watch_sam1.JPEG'),
        Product(name='갤럭시 워치6 클래식', price=429000, category='스마트워치', brand='삼성', stock=15,
                description='돌아온 회전 베젤의 클래식 감성', image_path='watch_sam2.JPEG'),
        Product(name='갤럭시 워치6', price=329000, category='스마트워치', brand='삼성', stock=25,
                description='더 커진 디스플레이, 얇아진 베젤', image_path='watch_sam3.JPEG'),
        Product(name='갤럭시 워치5 프로', price=499000, category='스마트워치', brand='삼성', stock=10,
                description='아웃도어에 최적화된 강력한 내구성', image_path='watch_sam4.JPEG'),
        Product(name='갤럭시 워치5', price=299000, category='스마트워치', brand='삼성', stock=30,
                description='매일의 건강을 기록하는 스마트 워치', image_path='watch_sam5.JPEG'),
        Product(name='갤럭시 워치4 클래식', price=299000, category='스마트워치', brand='삼성', stock=10,
                description='여전히 사랑받는 클래식 디자인', image_path='watch_sam6.JPEG'),
        Product(name='갤럭시 핏3', price=89000, category='스마트워치', brand='삼성', stock=50, description='가볍고 오래가는 스마트 밴드',
                image_path='watch_sam7.JPEG'),

        # --- 애플 (Apple) 8개 ---
        Product(name='Apple Watch Ultra 2', price=1149000, category='스마트워치', brand='애플', stock=10,
                description='가장 강인하고 뛰어난 성능의 애플워치', image_path='watch_app1.JPEG'),
        Product(name='Apple Watch Series 9', price=599000, category='스마트워치', brand='애플', stock=20,
                description='혁신적인 제스처 컨트롤 탑재', image_path='watch_app2.JPEG'),
        Product(name='Apple Watch SE (2세대)', price=329000, category='스마트워치', brand='애플', stock=30,
                description='부담 없이 시작하는 완벽한 애플워치', image_path='watch_app3.JPEG'),
        Product(name='Apple Watch Series 8', price=599000, category='스마트워치', brand='애플', stock=15,
                description='체온 센서와 충돌 감지 기능', image_path='watch_app4.JPEG'),
        Product(name='Apple Watch Ultra', price=1149000, category='스마트워치', brand='애플', stock=5,
                description='극한의 한계를 넘는 탐험가용', image_path='watch_app5.JPEG'),
        Product(name='Apple Watch Series 7', price=499000, category='스마트워치', brand='애플', stock=10,
                description='풀스크린의 몰입감', image_path='watch_app6.JPEG'),
        Product(name='Apple Watch Hermès', price=1699000, category='스마트워치', brand='애플', stock=3,
                description='에르메스만의 독보적인 우아함', image_path='watch_app7.JPEG'),
        Product(name='Apple Watch Nike', price=599000, category='스마트워치', brand='애플', stock=12,
                description='러너들을 위한 특별한 에디션', image_path='watch_app8.JPEG'),

        # --- 샤오미 (Xiaomi) 8개 ---
        Product(name='샤오미 워치 S3', price=169000, category='스마트워치', brand='샤오미', stock=20,
                description='교체 가능한 베젤, 나만의 스타일', image_path='watch_xia1.JPEG'),
        Product(name='샤오미 워치 2 프로', price=299000, category='스마트워치', brand='샤오미', stock=15,
                description='Wear OS 탑재 스마트워치', image_path='watch_xia2.JPEG'),
        Product(name='레드미 워치 4', price=99000, category='스마트워치', brand='샤오미', stock=35,
                description='압도적인 대화면 가성비 워치', image_path='watch_xia3.JPEG'),
        Product(name='레드미 워치 3 액티브', price=49000, category='스마트워치', brand='샤오미', stock=50,
                description='블루투스 통화까지 지원하는 입문용', image_path='watch_xia4.JPEG'),
        Product(name='샤오미 스마트 밴드 8 프로', price=79000, category='스마트워치', brand='샤오미', stock=40,
                description='밴드를 넘어선 스마트워치급 화면', image_path='watch_xia5.JPEG'),
        Product(name='샤오미 스마트 밴드 8', price=49000, category='스마트워치', brand='샤오미', stock=60,
                description='다양한 스타일링이 가능한 국민 밴드', image_path='watch_xia6.JPEG'),
        Product(name='샤오미 워치 S1 액티브', price=199000, category='스마트워치', brand='샤오미', stock=10,
                description='스포티한 디자인과 피트니스 기능', image_path='watch_xia7.JPEG'),
        Product(name='레드미 스마트 밴드 2', price=29000, category='스마트워치', brand='샤오미', stock=45,
                description='가볍게 즐기는 데일리 트래커', image_path='watch_xia8.jpg'),

        # --- 어메이즈핏 (Amazfit) 8개 ---
        Product(name='어메이즈핏 발란스', price=299000, category='스마트워치', brand='어메이즈핏', stock=15,
                description='라이프스타일과 웰니스의 완벽한 균형', image_path='watch_ama1.JPEG'),
        Product(name='어메이즈핏 팰컨', price=699000, category='스마트워치', brand='어메이즈핏', stock=5,
                description='티타늄 바디의 프리미엄 아웃도어 워치', image_path='watch_ama2.JPEG'),
        Product(name='어메이즈핏 티렉스 울트라', price=549000, category='스마트워치', brand='어메이즈핏', stock=10,
                description='궁극의 극한 환경용 스마트워치', image_path='watch_ama3.JPEG'),
        Product(name='어메이즈핏 액티브', price=179000, category='스마트워치', brand='어메이즈핏', stock=25,
                description='가볍고 스타일리시한 데일리 워치', image_path='watch_ama4.JPEG'),
        Product(name='어메이즈핏 치타 프로', price=399000, category='스마트워치', brand='어메이즈핏', stock=12,
                description='러너를 위한 정밀한 GPS 트래킹', image_path='watch_ama5.JPEG'),
        Product(name='어메이즈핏 GTR 4', price=269000, category='스마트워치', brand='어메이즈핏', stock=20,
                description='비즈니스와 스포츠를 아우르는 디자인', image_path='watch_ama6.JPEG'),
        Product(name='어메이즈핏 GTS 4', price=269000, category='스마트워치', brand='어메이즈핏', stock=20,
                description='초슬림 초경량의 스퀘어 워치', image_path='watch_ama7.JPEG'),
        Product(name='어메이즈핏 빕 5', price=119000, category='스마트워치', brand='어메이즈핏', stock=30,
                description='초대형 화면의 입문용 스마트워치', image_path='watch_ama8.JPEG'),

        # --- 가민 (Garmin) 8개 ---
        Product(name='가민 포러너 965', price=819000, category='스마트워치', brand='가민', stock=10,
                description='최상급 철인 3종 및 러닝 워치', image_path='watch_gar1.JPEG'),
        Product(name='가민 에픽스 프로', price=1390000, category='스마트워치', brand='가민', stock=5,
                description='아몰레드 디스플레이 탑재 프리미엄 아웃도어', image_path='watch_gar2.JPEG'),
        Product(name='가민 피닉스 7 프로', price=1290000, category='스마트워치', brand='가민', stock=8,
                description='태양광 충전 지원 최고의 멀티스포츠 워치', image_path='watch_gar3.JPEG'),
        Product(name='가민 베뉴 3', price=599000, category='스마트워치', brand='가민', stock=15,
                description='고급 피트니스 및 헬스 모니터링', image_path='watch_gar4.JPEG'),
        Product(name='가민 포러너 265', price=589000, category='스마트워치', brand='가민', stock=20,
                description='러너들의 가장 확실한 러닝 파트너', image_path='watch_gar5.jpg'),
        Product(name='가민 인스팅트 2X', price=599000, category='스마트워치', brand='가민', stock=12,
                description='강력한 내구성과 무한한 배터리', image_path='watch_gar6.JPEG'),
        Product(name='가민 비보액티브 5', price=429000, category='스마트워치', brand='가민', stock=25,
                description='가성비 좋은 데일리 피트니스 워치', image_path='watch_gar7.JPEG'),
        Product(name='가민 릴리 2', price=349000, category='스마트워치', brand='가민', stock=18,
                description='여성을 위한 작고 우아한 스마트워치', image_path='watch_gar8.JPEG'),
    ]

    # -------------------------------------------------------------------
    # 2-4. 대량의 태블릿 라인업 (40개)
    # -------------------------------------------------------------------
    other_tablets = [
        # --- 삼성 (Samsung) 8개 ---
        Product(name='갤럭시 탭 S9 울트라', price=1590000, category='태블릿', brand='삼성', stock=10,
                description='14.6인치 압도적 대화면의 끝판왕', image_path='tab_sam1.JPEG'),
        Product(name='갤럭시 탭 S9+', price=1240000, category='태블릿', brand='삼성', stock=15,
                description='완벽한 밸런스의 하이엔드 태블릿', image_path='tab_sam2.JPEG'),
        Product(name='갤럭시 탭 S9', price=990000, category='태블릿', brand='삼성', stock=20,
                description='가장 컴팩트한 다이내믹 AMOLED 2X', image_path='tab_sam3.JPEG'),
        Product(name='갤럭시 탭 S9 FE+', price=790000, category='태블릿', brand='삼성', stock=25,
                description='S펜과 대화면을 합리적인 가격에', image_path='tab_sam4.JPEG'),
        Product(name='갤럭시 탭 S9 FE', price=620000, category='태블릿', brand='삼성', stock=30,
                description='학생용 필기 머신으로 최적화', image_path='tab_sam5.JPEG'),
        Product(name='갤럭시 탭 S8 울트라', price=1100000, category='태블릿', brand='삼성', stock=5,
                description='여전히 현역인 전세대 최고스펙', image_path='tab_sam6.JPEG'),
        Product(name='갤럭시 탭 S8', price=750000, category='태블릿', brand='삼성', stock=12, description='부담없는 11인치 플래그십',
                image_path='tab_sam7.JPEG'),
        Product(name='갤럭시 탭 A9+', price=360000, category='태블릿', brand='삼성', stock=50,
                description='콘텐츠 감상과 인강용 가성비 탭', image_path='tab_sam8.JPEG'),

        # --- 애플 (Apple) 8개 ---
        Product(name='아이패드 프로 13 (M4)', price=1990000, category='태블릿', brand='애플', stock=8,
                description='M4 칩과 OLED로 무장한 역대급 프로', image_path='tab_app1.JPEG'),
        Product(name='아이패드 프로 11 (M4)', price=1490000, category='태블릿', brand='애플', stock=12,
                description='휴대성과 프로급 성능의 완벽한 조화', image_path='tab_app2.JPEG'),
        Product(name='아이패드 에어 13 (M2)', price=1190000, category='태블릿', brand='애플', stock=15,
                description='프로의 화면 크기를 에어의 가격으로', image_path='tab_app3.JPEG'),
        Product(name='아이패드 에어 11 (M2)', price=890000, category='태블릿', brand='애플', stock=20,
                description='누구에게나 추천하는 가장 대중적인 아이패드', image_path='tab_app4.JPEG'),
        Product(name='아이패드 미니 (6세대)', price=760000, category='태블릿', brand='애플', stock=18,
                description='한 손에 들어오는 강력한 아이패드', image_path='tab_app5.JPEG'),
        Product(name='아이패드 (10세대)', price=670000, category='태블릿', brand='애플', stock=30,
                description='전면 디자인 체인지, 팝한 컬러', image_path='tab_app6.JPEG'),
        Product(name='아이패드 (9세대)', price=490000, category='태블릿', brand='애플', stock=40,
                description='홈 버튼이 남아있는 최고의 가성비', image_path='tab_app7.JPEG'),
        Product(name='아이패드 프로 12.9 (6세대)', price=1720000, category='태블릿', brand='애플', stock=5,
                description='M2 칩 탑재 강력한 구형 프로', image_path='tab_app8.JPEG'),

        # --- 샤오미 (Xiaomi) 8개 ---
        Product(name='샤오미 패드 6S Pro 12.4', price=790000, category='태블릿', brand='샤오미', stock=15,
                description='PC급 생산성을 갖춘 샤오미 플래그십', image_path='tab_xia1.JPEG'),
        Product(name='샤오미 패드 6 프로', price=590000, category='태블릿', brand='샤오미', stock=10,
                description='게이밍도 거뜬한 스냅드래곤 8+ Gen 1', image_path='tab_xia2.JPEG'),
        Product(name='샤오미 패드 6', price=440000, category='태블릿', brand='샤오미', stock=25,
                description='안드로이드 가성비 태블릿의 기준', image_path='tab_xia3.JPEG'),
        Product(name='샤오미 패드 5', price=380000, category='태블릿', brand='샤오미', stock=12,
                description='여전히 잘 팔리는 전설의 명기', image_path='tab_xia4.JPEG'),
        Product(name='레드미 패드 프로', price=350000, category='태블릿', brand='샤오미', stock=30,
                description='12.1인치 대화면 레드미 패드', image_path='tab_xia5.JPEG'),
        Product(name='레드미 패드 SE 8.7', price=140000, category='태블릿', brand='샤오미', stock=50,
                description='한 손에 쏙 들어오는 초가성비 이북리더', image_path='tab_xia6.JPEG'),
        Product(name='레드미 패드 SE', price=200000, category='태블릿', brand='샤오미', stock=45,
                description='영상 시청용으로 완벽한 11인치', image_path='tab_xia7.JPEG'),
        Product(name='레드미 패드', price=250000, category='태블릿', brand='샤오미', stock=20,
                description='90Hz 주사율의 매끄러운 보급형', image_path='tab_xia8.JPEG'),

        # --- 레노버 (Lenovo) 8개 ---
        Product(name='레노버 리전 Y700 2세대', price=550000, category='태블릿', brand='레노버', stock=20,
                description='안드로이드 8인치 게이밍 끝판왕', image_path='tab_len1.JPEG'),
        Product(name='레노버 탭 P12 프로', price=990000, category='태블릿', brand='레노버', stock=5,
                description='12.6인치 AMOLED 프리미엄 탭', image_path='tab_len2.JPEG'),
        Product(name='레노버 탭 P12', price=400000, category='태블릿', brand='레노버', stock=25,
                description='가성비 12.7인치 대화면 필기 머신', image_path='tab_len3.JPEG'),
        Product(name='레노버 탭 P11 프로 2세대', price=500000, category='태블릿', brand='레노버', stock=15,
                description='120Hz OLED로 즐기는 완벽한 영상', image_path='tab_len4.JPEG'),
        Product(name='레노버 탭 P11 2세대', price=300000, category='태블릿', brand='레노버', stock=30,
                description='입문용 11인치 태블릿의 정석', image_path='tab_len5.JPEG'),
        Product(name='레노버 탭 M11', price=220000, category='태블릿', brand='레노버', stock=40,
                description='펜이 기본 포함된 교육용 가성비 패드', image_path='tab_len6.JPEG'),
        Product(name='레노버 탭 M10 플러스 3세대', price=250000, category='태블릿', brand='레노버', stock=35,
                description='인강용으로 최적화된 M시리즈', image_path='tab_len7.JPEG'),
        Product(name='레노버 요가 탭 13', price=700000, category='태블릿', brand='레노버', stock=10,
                description='킥스탠드와 마이크로 HDMI 지원의 유니크함', image_path='tab_len8.JPEG'),

        # --- 아이뮤즈 (iMUZ) 8개 ---
        Product(name='아이뮤즈 뮤패드 K13', price=299000, category='태블릿', brand='아이뮤즈', stock=30,
                description='압도적 가성비의 13인치 국내 브랜드 패드', image_path='tab_imuz1.JPEG'),
        Product(name='아이뮤즈 뮤패드 K10 PLUS', price=199000, category='태블릿', brand='아이뮤즈', stock=50,
                description='대란을 일으킨 10인치 초가성비 패드', image_path='tab_imuz2.JPEG'),
        Product(name='아이뮤즈 뮤패드 K11', price=229000, category='태블릿', brand='아이뮤즈', stock=40,
                description='더 넓어진 화면의 인강/영상 시청용', image_path='tab_imuz3.JPEG'),
        Product(name='아이뮤즈 레볼루션 G11', price=259000, category='태블릿', brand='아이뮤즈', stock=20,
                description='퍼포먼스를 조금 더 챙긴 11인치', image_path='tab_imuz4.jpg'),
        Product(name='아이뮤즈 뮤패드 L10', price=159000, category='태블릿', brand='아이뮤즈', stock=45,
                description='LTE 지원으로 언제 어디서나', image_path='tab_imuz5.JPEG'),
        Product(name='아이뮤즈 뮤패드 GS10', price=139000, category='태블릿', brand='아이뮤즈', stock=60,
                description='아이들 교육용, 영상 시청용 최적', image_path='tab_imuz6.jpg'),
        Product(name='아이뮤즈 컨버터 탭', price=359000, category='태블릿', brand='아이뮤즈', stock=15,
                description='도킹 키보드 지원으로 2-in-1 PC처럼', image_path='tab_imuz7.jpg'),
        Product(name='아이뮤즈 뮤패드 H10', price=119000, category='태블릿', brand='아이뮤즈', stock=55,
                description='부담없이 막 쓰기 좋은 기본형 패드', image_path='tab_imuz8.jpg'),
    ]

    # -------------------------------------------------------------------
    # 2-5. 대량의 노트북 라인업 (39개 - 기존 p4 포함 총 40개)
    # -------------------------------------------------------------------
    other_notebooks = [
        # --- 삼성 (Samsung) 8개 ---
        Product(name='갤럭시 북4 울트라', price=3200000, category='노트북', brand='삼성', stock=10,
                description='인텔 코어 울트라 9과 RTX 4070의 압도적 퍼포먼스', image_path='nb_sam1.JPEG'),
        Product(name='갤럭시 북4 프로 360', price=2500000, category='노트북', brand='삼성', stock=12,
                description='터치스크린과 S펜으로 확장되는 크리에이티브', image_path='nb_sam2.JPEG'),
        Product(name='갤럭시 북4 프로 16', price=2200000, category='노트북', brand='삼성', stock=20,
                description='가장 완벽한 밸런스의 AI 윈도우 노트북', image_path='nb_sam3.JPEG'),
        Product(name='갤럭시 북4 프로 14', price=1990000, category='노트북', brand='삼성', stock=18,
                description='극강의 휴대성을 자랑하는 14인치 프로', image_path='nb_sam4.JPEG'),
        Product(name='갤럭시 북4', price=1100000, category='노트북', brand='삼성', stock=30,
                description='대학생, 직장인을 위한 든든한 기본기', image_path='nb_sam5.JPEG'),
        Product(name='갤럭시 북3 프로 16', price=1600000, category='노트북', brand='삼성', stock=15,
                description='가성비가 되어버린 전세대 명기', image_path='nb_sam6.JPEG'),
        Product(name='갤럭시 북3 360', price=1450000, category='노트북', brand='삼성', stock=20,
                description='합리적인 가격에 만나는 2-in-1', image_path='nb_sam7.JPEG'),
        Product(name='삼성 노트북 플러스2', price=750000, category='노트북', brand='삼성', stock=40,
                description='인강 및 사무용으로 최적화된 실속형', image_path='nb_sam8.JPEG'),

        # --- 애플 (Apple) 7개 (기존 p4 포함 8개) ---
        Product(name='맥북 프로 16 (M3 Max)', price=4890000, category='노트북', brand='애플', stock=5,
                description='전문가를 위한 괴물 같은 성능과 배터리', image_path='nb_app1.JPEG'),
        Product(name='맥북 프로 14 (M3 Pro)', price=2990000, category='노트북', brand='애플', stock=10,
                description='휴대성과 프로급 성능을 동시에', image_path='nb_app2.JPEG'),
        Product(name='맥북 프로 14 (M3)', price=2390000, category='노트북', brand='애플', stock=15,
                description='더 많은 사용자를 위한 새로운 프로의 기준', image_path='nb_app3.JPEG'),
        Product(name='맥북 에어 15 (M3)', price=1890000, category='노트북', brand='애플', stock=20,
                description='크고 아름다운 화면, 놀라운 두께', image_path='nb_app4.JPEG'),
        Product(name='맥북 에어 13 (M2)', price=1390000, category='노트북', brand='애플', stock=35,
                description='가장 사랑받는 애플 노트북의 베스트셀러', image_path='nb_app5.JPEG'),
        Product(name='맥북 프로 16 (M2 Max)', price=3990000, category='노트북', brand='애플', stock=3,
                description='여전히 강력한 하이엔드 영상 편집 머신', image_path='nb_app6.JPEG'),
        Product(name='맥북 에어 13 (M1)', price=990000, category='노트북', brand='애플', stock=12,
                description='세상을 놀라게 한 전설의 시작', image_path='nb_app7.JPEG'),

        # --- 레노버 (Lenovo) 8개 ---
        Product(name='씽크패드 X1 카본 Gen 12', price=2790000, category='노트북', brand='레노버', stock=10,
                description='비즈니스 노트북의 영원한 아이콘', image_path='nb_len1.JPEG'),
        Product(name='리전 프로 7i', price=3490000, category='노트북', brand='레노버', stock=5,
                description='타협 없는 하이엔드 게이밍 노트북', image_path='nb_len2.JPEG'),
        Product(name='요가 슬림 7i', price=1590000, category='노트북', brand='레노버', stock=15,
                description='고급스러운 알루미늄 바디와 OLED', image_path='nb_len3.JPEG'),
        Product(name='리전 슬림 5', price=1790000, category='노트북', brand='레노버', stock=20,
                description='휴대성과 성능을 다 잡은 올라운더', image_path='nb_len4.JPEG'),
        Product(name='로크(LOQ) 15', price=1290000, category='노트북', brand='레노버', stock=25,
                description='게이밍 노트북 입문자를 위한 완벽한 선택', image_path='nb_len5.JPEG'),
        Product(name='아이디어패드 슬림 5', price=890000, category='노트북', brand='레노버', stock=40,
                description='가성비 노트북 1티어 베스트셀러', image_path='nb_len6.JPEG'),
        Product(name='씽크북 16', price=1090000, category='노트북', brand='레노버', stock=20,
                description='가성비와 보안을 모두 챙긴 기업용', image_path='nb_len7.JPEG'),
        Product(name='아이디어패드 플렉스 5', price=950000, category='노트북', brand='레노버', stock=18,
                description='태블릿처럼 쓰는 가성비 2-in-1', image_path='nb_len8.JPEG'),

        # --- LG (lg) 8개 ---
        Product(name='LG 그램 프로 16', price=2390000, category='노트북', brand='lg', stock=15,
                description='가벼움에 외장 그래픽 성능을 더하다', image_path='nb_lg1.JPEG'),
        Product(name='LG 그램 17', price=2150000, category='노트북', brand='lg', stock=20,
                description='17인치 대화면을 이렇게 가볍게', image_path='nb_lg2.JPEG'),
        Product(name='LG 그램 16', price=1890000, category='노트북', brand='lg', stock=25,
                description='대한민국 표준 16인치 초경량 노트북', image_path='nb_lg3.JPEG'),
        Product(name='LG 그램 15', price=1690000, category='노트북', brand='lg', stock=12,
                description='익숙한 비율, 변함없는 가벼움', image_path='nb_lg4.JPEG'),
        Product(name='LG 그램 14', price=1550000, category='노트북', brand='lg', stock=30,
                description='이동이 많은 대학생에게 딱 맞는 1kg 미만', image_path='nb_lg5.JPEG'),
        Product(name='LG 울트라PC 15', price=950000, category='노트북', brand='lg', stock=40,
                description='그램의 감성을 담은 실속형 대화면', image_path='nb_lg6.JPEG'),
        Product(name='LG 그램 360 16', price=2250000, category='노트북', brand='lg', stock=8,
                description='360도 회전 힌지와 터치펜의 유연함', image_path='nb_lg7.JPEG'),
        Product(name='LG 울트라기어 17', price=2590000, category='노트북', brand='lg', stock=5,
                description='LG가 만든 쾌적한 고성능 게이밍 머신', image_path='nb_lg8.JPEG'),

        # --- ASUS (ASUS) 8개 ---
        Product(name='ROG 스트릭스 스카 18', price=4590000, category='노트북', brand='ASUS', stock=3,
                description='18인치 데스크탑 대체용 최상위 게이밍', image_path='nb_asus1.JPEG'),
        Product(name='ROG 제피러스 G14', price=2590000, category='노트북', brand='ASUS', stock=10,
                description='가장 스타일리시한 14인치 게이밍', image_path='nb_asus2.JPEG'),
        Product(name='젠북 14 OLED', price=1490000, category='노트북', brand='ASUS', stock=20,
                description='아름다운 OLED 화면과 초경량 메탈 바디', image_path='nb_asus3.JPEG'),
        Product(name='비보북 프로 15 OLED', price=1390000, category='노트북', brand='ASUS', stock=25,
                description='크리에이터를 위한 압도적 가성비', image_path='nb_asus4.JPEG'),
        Product(name='TUF 게이밍 A15', price=1350000, category='노트북', brand='ASUS', stock=30,
                description='밀리터리 등급 내구성과 극강의 게이밍 가성비', image_path='nb_asus5.JPEG'),
        Product(name='비보북 고 15', price=550000, category='노트북', brand='ASUS', stock=50,
                description='웹서핑, 인강용으로 완벽한 가성비 1위', image_path='nb_asus6.JPEG'),
        Product(name='엑스퍼트북 B9', price=1990000, category='노트북', brand='ASUS', stock=8,
                description='비즈니스 프로페셔널을 위한 초경량 노트북', image_path='nb_asus7.JPEG'),
        Product(name='ROG 플로우 X13', price=2190000, category='노트북', brand='ASUS', stock=5,
                description='360도 회전하는 초소형 게이밍 2-in-1', image_path='nb_asus8.JPEG'),
    ]

    # -------------------------------------------------------------------
    # 2-6. 대량의 헤드폰 라인업 (39개 - 기존 p3 포함 총 40개)
    # -------------------------------------------------------------------
    other_headphones = [
        # --- 소니 (Sony) 7개 (기존 p3 포함 총 8개) ---
        Product(name='WH-1000XM5', price=479000, category='헤드폰', brand='소니', stock=15,
                description='업계 최고 수준의 노이즈 캔슬링', image_path='hp_sony1.jpg'),
        Product(name='WH-1000XM4', price=399000, category='헤드폰', brand='소니', stock=20,
                description='여전히 사랑받는 스테디셀러 명기', image_path='hp_sony2.jpg'),
        Product(name='ULT WEAR', price=259000, category='헤드폰', brand='소니', stock=25, description='심장을 울리는 압도적인 베이스',
                image_path='hp_sony3.jpg'),
        Product(name='WH-CH720N', price=159000, category='헤드폰', brand='소니', stock=30,
                description='가장 가벼운 소니의 노이즈 캔슬링', image_path='hp_sony4.jpg'),
        Product(name='WH-CH520', price=89000, category='헤드폰', brand='소니', stock=50, description='부담 없이 즐기는 데일리 헤드폰',
                image_path='hp_sony5.jpg'),
        Product(name='INZONE H9', price=349000, category='헤드폰', brand='소니', stock=10,
                description='승리를 위한 프리미엄 게이밍 헤드셋', image_path='hp_sony6.jpg'),
        Product(name='MDR-MV1', price=499000, category='헤드폰', brand='소니', stock=5,
                description='크리에이터를 위한 오픈형 레퍼런스 모니터', image_path='hp_sony7.jpg'),

        # --- 애플 & 비츠 (Apple / Beats) 8개 ---
        Product(name='AirPods Max', price=769000, category='헤드폰', brand='애플', stock=10,
                description='원음 구현 하이파이 오디오와 아름다운 디자인', image_path='hp_app1.jpg'),
        Product(name='Beats Studio Pro', price=449000, category='헤드폰', brand='애플', stock=15,
                description='무손실 오디오를 지원하는 비츠의 플래그십', image_path='hp_app2.jpg'),
        Product(name='Beats Solo 4', price=269000, category='헤드폰', brand='애플', stock=25,
                description='공간 음향으로 업그레이드된 온이어 아이콘', image_path='hp_app3.jpg'),
        Product(name='Beats Solo 3 Wireless', price=209000, category='헤드폰', brand='애플', stock=30,
                description='최대 40시간 재생, 지치지 않는 배터리', image_path='hp_app4.jpg'),
        Product(name='Beats Studio 3 Wireless', price=350000, category='헤드폰', brand='애플', stock=8,
                description='Pure ANC가 선사하는 고품격 사운드', image_path='hp_app5.jpg'),
        Product(name='Beats EP', price=119000, category='헤드폰', brand='애플', stock=40,
                description='비츠 사운드 입문자를 위한 유선 모델', image_path='hp_app6.jpg'),
        Product(name='Beats Pro', price=490000, category='헤드폰', brand='애플', stock=5,
                description='음향 전문가와 DJ를 위한 알루미늄 바디', image_path='hp_app7.jpg'),
        Product(name='AirPods Max (USB-C)', price=769000, category='헤드폰', brand='애플', stock=12,
                description='USB-C로 더욱 편리해진 새로운 색상의 맥스', image_path='hp_app8.jpg'),

        # --- 보스 (Bose) 8개 ---
        Product(name='QuietComfort Ultra Headphones', price=499000, category='헤드폰', brand='보스', stock=15,
                description='몰입형 오디오와 최상급 노이즈 캔슬링', image_path='hp_bose1.jpg'),
        Product(name='QuietComfort Headphones', price=389000, category='헤드폰', brand='보스', stock=20,
                description='전설적인 QC 라인업의 새로운 기준', image_path='hp_bose2.jpg'),
        Product(name='QuietComfort 45', price=350000, category='헤드폰', brand='보스', stock=18,
                description='가벼운 무게, 부드러운 착용감의 정석', image_path='hp_bose3.jpg'),
        Product(name='QuietComfort SE', price=320000, category='헤드폰', brand='보스', stock=25,
                description='소프트 케이스로 합리성을 더한 QC45', image_path='hp_bose4.jpg'),
        Product(name='Noise Cancelling Headphones 700', price=450000, category='헤드폰', brand='보스', stock=10,
                description='세련된 디자인과 11단계 노이즈 제어', image_path='hp_bose5.jpg'),
        Product(name='SoundLink Around-Ear II', price=299000, category='헤드폰', brand='보스', stock=30,
                description='언제 어디서나 편안한 무선 사운드', image_path='hp_bose6.jpg'),
        Product(name='QuietComfort 35 II Gaming', price=420000, category='헤드폰', brand='보스', stock=5,
                description='게이머를 위한 보스의 노캔 마이크 에디션', image_path='hp_bose7.jpg'),
        Product(name='A30 Aviation Headset', price=1500000, category='헤드폰', brand='보스', stock=2,
                description='항공 전문가를 위한 최상위 파일럿 헤드셋', image_path='hp_bose8.jpg'),

        # --- JBL 8개 ---
        Product(name='Tour One M2', price=399000, category='헤드폰', brand='JBL', stock=12,
                description='트루 어댑티브 노이즈 캔슬링과 공간 음향', image_path='hp_jbl1.jpg'),
        Product(name='Live 770NC', price=229000, category='헤드폰', brand='JBL', stock=20,
                description='JBL 시그니처 사운드가 담긴 패브릭 헤드밴드', image_path='hp_jbl2.jpg'),
        Product(name='Live 670NC', price=179000, category='헤드폰', brand='JBL', stock=25,
                description='가볍게 귀에 얹는 온이어 노이즈 캔슬링', image_path='hp_jbl3.jpg'),
        Product(name='Tune 770NC', price=139000, category='헤드폰', brand='JBL', stock=35,
                description='입문용으로 완벽한 가성비 노이즈 캔슬링', image_path='hp_jbl4.jpg'),
        Product(name='Tune 720BT', price=89000, category='헤드폰', brand='JBL', stock=45,
                description='최대 76시간 연속 재생의 든든한 무선 헤드폰', image_path='hp_jbl5.jpg'),
        Product(name='Tune 520BT', price=59000, category='헤드폰', brand='JBL', stock=60,
                description='퓨어 베이스 사운드의 초가성비 모델', image_path='hp_jbl6.jpg'),
        Product(name='Quantum 910 Wireless', price=349000, category='헤드폰', brand='JBL', stock=10,
                description='헤드 트래킹을 지원하는 게이밍 끝판왕', image_path='hp_jbl7.jpg'),
        Product(name='Quantum 350 Wireless', price=119000, category='헤드폰', brand='JBL', stock=25,
                description='무손실 2.4GHz 무선 게이밍 헤드셋', image_path='hp_jbl8.jpg'),

        # --- 젠하이저 (Sennheiser) 8개 ---
        Product(name='Momentum 4 Wireless', price=479000, category='헤드폰', brand='젠하이저', stock=15,
                description='60시간 배터리와 독보적인 오디오 파일 사운드', image_path='hp_sen1.jpg'),
        Product(name='Accentum Plus Wireless', price=329000, category='헤드폰', brand='젠하이저', stock=20,
                description='터치 컨트롤과 어댑티브 노캔의 영리함', image_path='hp_sen2.jpg'),
        Product(name='Accentum Wireless', price=249000, category='헤드폰', brand='젠하이저', stock=25,
                description='모멘텀의 DNA를 이어받은 훌륭한 엔트리', image_path='hp_sen3.jpg'),
        Product(name='HD 450BT', price=199000, category='헤드폰', brand='젠하이저', stock=30,
                description='클래식한 디자인의 가성비 노이즈 캔슬링', image_path='hp_sen4.jpg'),
        Product(name='HD 350BT', price=139000, category='헤드폰', brand='젠하이저', stock=40,
                description='단단한 베이스와 깨끗한 고음', image_path='hp_sen5.jpg'),
        Product(name='HD 600', price=549000, category='헤드폰', brand='젠하이저', stock=8,
                description='오픈형 레퍼런스 헤드폰의 살아있는 전설', image_path='hp_sen6.jpg'),
        Product(name='HD 660S2', price=799000, category='헤드폰', brand='젠하이저', stock=5,
                description='더 깊어진 저음으로 완성된 궁극의 사운드', image_path='hp_sen7.jpg'),
        Product(name='RS 175', price=379000, category='헤드폰', brand='젠하이저', stock=12,
                description='TV 시청과 홈시네마를 위한 완벽한 무선 시스템', image_path='hp_sen8.jpg'),
    ]

    # -------------------------------------------------------------------
    # 2-7. 대량의 블루투스 스피커 라인업 (40개)
    # -------------------------------------------------------------------
    other_speakers = [
        # --- JBL 8개 ---
        Product(name='JBL GO 3', price=49000, category='블루투스 스피커', brand='JBL', stock=50,
                description='한 손에 쏙 들어오는 방수방진 캠핑 스피커', image_path='spk_jbl1.jpg'),
        Product(name='JBL Flip 6', price=129000, category='블루투스 스피커', brand='JBL', stock=40,
                description='세워도 눕혀도 완벽한 아웃도어 사운드', image_path='spk_jbl2.jpg'),
        Product(name='JBL Charge 5', price=199000, category='블루투스 스피커', brand='JBL', stock=30,
                description='보조배터리 기능이 탑재된 강력한 스피커', image_path='spk_jbl3.jpg'),
        Product(name='JBL Pulse 5', price=279000, category='블루투스 스피커', brand='JBL', stock=20,
                description='음악에 맞춰 춤추는 360도 LED 라이트쇼', image_path='spk_jbl4.jpg'),
        Product(name='JBL Xtreme 3', price=349000, category='블루투스 스피커', brand='JBL', stock=15,
                description='스트랩으로 메고 다니는 파티용 붐박스', image_path='spk_jbl5.jpg'),
        Product(name='JBL Boombox 3', price=549000, category='블루투스 스피커', brand='JBL', stock=5,
                description='가슴을 울리는 극강의 베이스 퍼포먼스', image_path='spk_jbl6.jpg'),
        Product(name='JBL Clip 4', price=69000, category='블루투스 스피커', brand='JBL', stock=45,
                description='가방에 툭 걸고 떠나는 등산 필수템', image_path='spk_jbl7.jpg'),
        Product(name='JBL Authentics 200', price=449000, category='블루투스 스피커', brand='JBL', stock=10,
                description='클래식한 레트로 디자인과 스마트홈의 만남', image_path='spk_jbl8.jpg'),

        # --- 소니 (Sony) 8개 ---
        Product(name='SRS-XB100', price=79000, category='블루투스 스피커', brand='소니', stock=40,
                description='작지만 맑고 강력한 확산형 사운드', image_path='spk_sony1.jpg'),
        Product(name='SRS-XE200', price=149000, category='블루투스 스피커', brand='소니', stock=30,
                description='라인 디퓨저 기술로 넓게 퍼지는 소리', image_path='spk_sony2.jpg'),
        Product(name='SRS-XE300', price=199000, category='블루투스 스피커', brand='소니', stock=25,
                description='어디서든 동일한 고음질 사운드 경험', image_path='spk_sony3.jpg'),
        Product(name='SRS-XG300', price=299000, category='블루투스 스피커', brand='소니', stock=15,
                description='접이식 손잡이와 화려한 라이팅', image_path='spk_sony4.jpg'),
        Product(name='LSPX-S3', price=399000, category='블루투스 스피커', brand='소니', stock=10,
                description='공간을 은은하게 채우는 글래스 사운드', image_path='spk_sony5.jpg'),
        Product(name='SRS-XV800', price=699000, category='블루투스 스피커', brand='소니', stock=5,
                description='TV 연결까지 지원하는 파티용 대형 스피커', image_path='spk_sony6.jpg'),
        Product(name='SRS-XB23', price=119000, category='블루투스 스피커', brand='소니', stock=35,
                description='텀블러 디자인의 컴팩트 아웃도어 스피커', image_path='spk_sony7.jpg'),
        Product(name='HT-AX7', price=699000, category='블루투스 스피커', brand='소니', stock=8,
                description='3개의 스피커로 완성하는 포터블 시어터', image_path='spk_sony8.jpg'),

        # --- 보스 (Bose) 8개 ---
        Product(name='SoundLink Micro', price=139000, category='블루투스 스피커', brand='보스', stock=30,
                description='자전거, 백팩 어디든 매달 수 있는 견고함', image_path='spk_bose1.jpg'),
        Product(name='SoundLink Flex', price=179000, category='블루투스 스피커', brand='보스', stock=40,
                description='자세에 맞춰 사운드를 자동 최적화', image_path='spk_bose2.jpg'),
        Product(name='SoundLink Mini II SE', price=239000, category='블루투스 스피커', brand='보스', stock=25,
                description='보스 블루투스 스피커의 영원한 베스트셀러', image_path='spk_bose3.jpg'),
        Product(name='SoundLink Revolve II', price=279000, category='블루투스 스피커', brand='보스', stock=20,
                description='사각지대 없는 완벽한 360도 사운드', image_path='spk_bose4.jpg'),
        Product(name='SoundLink Revolve+ II', price=389000, category='블루투스 스피커', brand='보스', stock=15,
                description='더 크고 깊어진 360도 프리미엄 사운드', image_path='spk_bose5.jpg'),
        Product(name='SoundLink Max', price=549000, category='블루투스 스피커', brand='보스', stock=10,
                description='파티를 압도하는 보스의 가장 큰 포터블', image_path='spk_bose6.jpg'),
        Product(name='Portable Smart Speaker', price=459000, category='블루투스 스피커', brand='보스', stock=8,
                description='집안과 밖을 아우르는 Wi-Fi & 블루투스', image_path='spk_bose7.jpg'),
        Product(name='S1 Pro+', price=990000, category='블루투스 스피커', brand='보스', stock=3,
                description='버스킹과 강연을 위한 무선 올인원 PA 시스템', image_path='spk_bose8.jpg'),

        # --- 브리츠 (Britz) 8개 ---
        Product(name='BZ-B1', price=79900, category='블루투스 스피커', brand='브리츠', stock=50,
                description='레트로 감성의 리얼 우드 인테리어 탁상용 라디오 스피커', image_path='spk_britz1.jpg'),

        Product(name='BZ-WX3', price=69900, category='블루투스 스피커', brand='브리츠', stock=20,
                description='캠핑에 제격인 TWS 지원 LED 무드등 블루투스 스피커', image_path='spk_britz2.jpg'),

        Product(name='BZ-TK3', price=55000, category='블루투스 스피커', brand='브리츠', stock=60,
                description='IPX4 생활방수와 화려한 LED 조명을 품은 아웃도어 스피커', image_path='spk_britz3.jpg'),

        Product(name='BZ-TK1', price=25000, category='블루투스 스피커', brand='브리츠', stock=45,
                description='유니크한 음료 캔 디자인과 히든 스트랩을 갖춘 휴대용 스피커', image_path='spk_britz4.jpg'),

        Product(name='BZ-MK88', price=56000, category='블루투스 스피커', brand='브리츠', stock=35,
                description='라디오, 시계, 알람 기능까지 품은 올인원 우든 탁상용 스피커', image_path='spk_britz5.jpg'),

        Product(name='BZ-MV5000', price=75900, category='블루투스 스피커', brand='브리츠', stock=40,
                description='클래식한 턴테이블을 연상시키는 레트로 디자인 스피커', image_path='spk_britz6.jpg'),

        Product(name='BZ-MQ5', price=86900, category='블루투스 스피커', brand='브리츠', stock=15,
                description='라디오와 시계가 더해진 손잡이 일체형 감성 블루투스 스피커', image_path='spk_britz7.jpg'),

        Product(name='BZ-JB6800', price=195000, category='블루투스 스피커', brand='브리츠', stock=30,
                description='압도적인 고출력을 자랑하는 프리미엄 앤틱 스테레오 스피커', image_path='spk_britz8.jpg'),

        # --- LG (lg) 8개 ---
        Product(name='XBOOM 360 XO3Q', price=299000, category='블루투스 스피커', brand='lg', stock=15,
                description='오브제처럼 아름다운 360도 무지향성 스피커', image_path='spk_lg1.jpg'),
        Product(name='XBOOM 360 RP4', price=359000, category='블루투스 스피커', brand='lg', stock=10,
                description='고급스러운 램프 디자인의 공간 음향', image_path='spk_lg2.jpg'),
        Product(name='XBOOM Go XG7Q', price=189000, category='블루투스 스피커', brand='lg', stock=20,
                description='트랙형 우퍼로 더 단단해진 사운드', image_path='spk_lg3.jpg'),
        Product(name='XBOOM Go XG5Q', price=129000, category='블루투스 스피커', brand='lg', stock=25,
                description='야외 활동에 최적화된 엣지 라이팅', image_path='spk_lg4.jpg'),
        Product(name='XBOOM Go XG9Q', price=449000, category='블루투스 스피커', brand='lg', stock=5,
                description='폭발적인 출력과 화려한 스테이지 라이팅', image_path='spk_lg5.jpg'),
        Product(name='XBOOM Go PL7', price=159000, category='블루투스 스피커', brand='lg', stock=18,
                description='메리디안 오디오 기술이 적용된 프리미엄 소리', image_path='spk_lg6.jpg'),
        Product(name='XBOOM Go PL5', price=109000, category='블루투스 스피커', brand='lg', stock=30,
                description='적당한 크기와 세련된 무빙 라이트', image_path='spk_lg7.jpg'),
        Product(name='XBOOM Go PL2', price=59000, category='블루투스 스피커', brand='lg', stock=40,
                description='한 손에 들어오는 가벼운 메리디안 사운드', image_path='spk_lg8.jpg'),
    ]

    # -------------------------------------------------------------------
    # 3. 모든 상품을 DB에 올리고 커밋
    # -------------------------------------------------------------------
    db.session.add_all([p1, p2, p3, p4, p5] + other_smartphones + other_earphones + other_smartwatches + other_tablets + other_notebooks + other_headphones + other_speakers)
    db.session.commit()

    print("📦 상품 기본 데이터 생성 완료, 옵션 매칭 시작...")

    # 2. 제품별 상세 옵션(ProductOption) 생성
    options = [
        # --- 갤럭시 S26 울트라 (p1) ---
        ProductOption(product_id=p1.id, otype='모델', oname='갤럭시 S26 울트라 (174.9mm)', add_price=0),
        ProductOption(product_id=p1.id, otype='용량', oname='256GB ㅣ 12GB', add_price=0),
        ProductOption(product_id=p1.id, otype='용량', oname='512GB ㅣ 12GB', add_price=253000),
        ProductOption(product_id=p1.id, otype='용량', oname='1TB ㅣ 16GB', add_price=748000),
        ProductOption(product_id=p1.id, otype='색상', oname='핑크 골드', color_code='#F1DDCF',
                      image_variant='phone1_pink.jpg'),
        ProductOption(product_id=p1.id, otype='색상', oname='실버 쉐도우', color_code='#C0C0C0',
                      image_variant='phone1_silver.jpg'),
        ProductOption(product_id=p1.id, otype='색상', oname='블랙', color_code='#000000', image_variant='phone1_black.jpg'),
        ProductOption(product_id=p1.id, otype='색상', oname='블루', color_code='#A2B5CD', image_variant='phone1_blue.jpg'),

        # --- 애플 에어팟 (p2) - 케이스 옵션 예시 ---
        ProductOption(product_id=p2.id, otype='모델', oname='유선 충전 모델', add_price=0),
        ProductOption(product_id=p2.id, otype='모델', oname='MagSafe 충전 모델', add_price=50000),

        # --- 소니 WH 헤드폰 (p3) ---
        ProductOption(product_id=p3.id, otype='색상', oname='플래티넘 실버', color_code='#E5E5E5',
                      image_variant='headphone1_silver.jpg'),
        ProductOption(product_id=p3.id, otype='색상', oname='블랙', color_code='#1A1A1A',
                      image_variant='headphone1_black.jpg'),
        ProductOption(product_id=p3.id, otype='색상', oname='미드나잇 블루', color_code='#191970',
                      image_variant='headphone1_blue.jpg'),

        # --- 맥북 에어 M3 (p4) ---
        ProductOption(product_id=p4.id, otype='모델', oname='13 모델', add_price=0),
        ProductOption(product_id=p4.id, otype='모델', oname='15 모델', add_price=300000),
        ProductOption(product_id=p4.id, otype='색상', oname='스타라이트', color_code='#F0EAD6',
                      image_variant='notebook2_starlight.jpg'),
        ProductOption(product_id=p4.id, otype='색상', oname='미드나잇', color_code='#2C3539',
                      image_variant='notebook2_midnight.jpg'),
        ProductOption(product_id=p4.id, otype='칩셋', oname='8코어 GPU', add_price=0),
        ProductOption(product_id=p4.id, otype='칩셋', oname='10코어 GPU', add_price=150000),

        # --- 갤럭시 워치 8 (p5) ---
        ProductOption(product_id=p5.id, otype='모델', oname='갤럭시 워치8', add_price=0),
        ProductOption(product_id=p5.id, otype='모델', oname='갤럭시 워치8 클래식', add_price=100000),
        ProductOption(product_id=p5.id, otype='크기', oname='40mm', add_price=0),
        ProductOption(product_id=p5.id, otype='크기', oname='44mm', add_price=50000),
        ProductOption(product_id=p5.id, otype='색상', oname='그라파이트', color_code='#383838',
                      image_variant='watch1_graphite.jpg'),
        ProductOption(product_id=p5.id, otype='색상', oname='실버', color_code='#C0C0C0',
                      image_variant='watch1_silver.jpg'),
    ]

    # 3. 옵션 일괄 추가 및 최종 커밋
    db.session.add_all(options)
    db.session.commit()

    print("✅ 모든 상품 옵션 데이터 통합 완료!")

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
                # 🌟 멤버십 회원: 10% 쿠폰(amount=10) + 3,000원 쿠폰
                db.session.add(Coupon(user_id=user_obj.id, name='멤버십 전용 10% 할인쿠폰', discount_amount=10))
                db.session.add(Coupon(user_id=user_obj.id, name='가입 축하 3,000원 할인쿠폰', discount_amount=3000))
            else:
                # 🌟 일반 회원: 3% 쿠폰(amount=3) + 1,000원 쿠폰
                db.session.add(Coupon(user_id=user_obj.id, name='일반 회원 3% 할인쿠폰', discount_amount=3))
                db.session.add(Coupon(user_id=user_obj.id, name='가입 축하 1,000원 할인쿠폰', discount_amount=1000))

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

    # ==========================================
    # Phase 4. 자동 리뷰 생성 (Review)
    # ==========================================
    print("📝 상품별 그럴싸한 리뷰 데이터를 13개씩 생성하는 중...")

    REVIEW_CONTENTS = [
        "배송이 빠르고 물건이 너무 좋아요! 완전 만족합니다.",
        "가성비 최고입니다. 이 가격에 이 퀄리티라니 놀랍네요.",
        "디자인이 실물이 훨씬 예쁘고 마음에 듭니다.",
        "지인에게 선물했는데 아주 좋아하네요. 뿌듯합니다.",
        "포장도 꼼꼼하고 품질도 기대 이상으로 만족스럽습니다.",
        "생각보다 훨씬 좋네요. 앞으로 잘 쓰겠습니다!",
        "기대했던 것만큼 훌륭합니다. 믿고 구매하길 잘했네요.",
        "색상이 화면과 같고 정말 예뻐요. 강추합니다.",
        "작동이 부드럽고 성능이 우수합니다. 역시 최고네요.",
        "배송은 조금 걸렸지만, 상품이 좋아서 용서가 됩니다.",
        "벌써 두 번째 구매입니다. 재구매 의사 100% 입니다!",
        "가격 대비 아주 훌륭한 제품입니다. 주변에 추천하고 있어요.",
        "매일 아주 잘 사용하고 있습니다. 삶의 질이 올라갔어요!",
        "마감 처리가 아주 깔끔하고 고급스럽습니다. 만족해요.",
        "고민하다 샀는데 진작 살 걸 그랬어요. 너무 좋습니다."
    ]

    # 앞서 만들어둔 모든 유저와 상품을 불러옵니다.
    all_users = User.query.all()
    all_products = Product.query.all()

    reviews_added = 0
    for product in all_products:
        # 27명의 유저 리스트를 무작위로 섞은 뒤, 앞의 13명만 뽑습니다 (1인 1리뷰 원칙 준수!)
        random.shuffle(all_users)
        selected_users = all_users[:13]

        for i in range(13):
            # 4~5점 위주의 별점 세팅
            rating = random.choices([5, 4, 3], weights=[70, 20, 10])[0]
            content = random.choice(REVIEW_CONTENTS)
            # 최근 90일 이내의 랜덤 날짜
            random_days = random.randint(0, 90)
            random_time = datetime.utcnow() - timedelta(days=random_days)

            review = Review(
                product_id=product.id,
                user_id=selected_users[i].id,
                content=content,
                rating=rating,
                image_path=None,
                timestamp=random_time
            )
            db.session.add(review)
            reviews_added += 1

    # 🔥 진짜 최종 4차 커밋
    db.session.commit()
    print(f"🎉 성공! 모든 상품에 리뷰가 13개씩 세팅되었습니다. (총 {reviews_added}개 추가됨)")
    print("🏆 ConnectShop 데이터베이스 초기 세팅 완벽 종료!")