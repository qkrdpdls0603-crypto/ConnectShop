# ConnectShop 폴더 안에 있는 데이터베이스 관리자(db)를 불러옵니다.
from ConnectShop import db
# 주문 시간, 리뷰 작성 시간 등을 기록하기 위해 파이썬의 시간 도구를 불러옵니다.
from datetime import datetime, timezone

# =========================================================
# [팀원 2: 김도철님 담당] 회원 및 멤버십 그룹
# =========================================================

# 1. 회원(User) 테이블: 우리 쇼핑몰에 가입한 고객들의 명부입니다.
class User(db.Model):
    # id: 각 회원을 구분하는 고유 번호입니다. (예: 1번 회원, 2번 회원 / primary_key=True 는 이 값이 겹치지 않는 핵심 번호라는 뜻)
    id = db.Column(db.Integer, primary_key=True)
    # username: 회원의 이름(또는 아이디)입니다. (unique=True: 동명이인/중복 불가, nullable=False: 필수 입력)
    username = db.Column(db.String(150), unique=True, nullable=False)
    # password: 암호화되어 저장될 비밀번호입니다. (필수 입력)
    password = db.Column(db.String(200), nullable=False)
    # email: 이메일 주소입니다. (중복 불가, 필수 입력)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # phone: 전화번호입니다.
    phone = db.Column(db.String(15),  nullable=False)
    # is_membership: 유료 멤버십 회원인지 일반 회원인지 구분합니다. (default=False: 가입 시 기본적으로 일반 회원)
    is_membership = db.Column(db.Boolean, default=False)
    # join_date: 회원가입을 한 날짜와 시간입니다. (현재 시간이 자동으로 들어갑니다)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)

    # join_date 컬럼 바로 아래에 이 함수를 하나만 남기면 됩니다.
    def __repr__(self):
        return f'<User {self.username}>'

# =========================================================
# 2. 멤버십 혜택(MembershipBenefit) 테이블: 멤버십 회원이 가진 특별한 혜택 정보입니다.
# =========================================================
class MembershipBenefit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # user_id: '누구의 혜택인가?'를 알기 위해 User 테이블의 id를 연결(ForeignKey)합니다.
    # ondelete='CASCADE': 회원이 탈퇴(삭제)하면, 이 혜택 정보도 찌꺼기로 남지 않고 같이 삭제하라는 뜻입니다.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    # has_apple_care: 애플케어 같은 보증 혜택이 있는지 여부
    has_apple_care = db.Column(db.Boolean, default=False)
    # free_shipping: 무료 배송 혜택이 있는지 여부
    free_shipping = db.Column(db.Boolean, default=False)
    # user: 파이썬 코드 안에서 '혜택.user'라고 치면 바로 해당 회원 정보를 가져올 수 있게 묶어주는 가상의 끈입니다. (1:1 관계)
    user = db.relationship('User', backref=db.backref('benefit', uselist=False))

# 3. 쿠폰(Coupon) 테이블: 회원이 보유한 할인 쿠폰들입니다.
class Coupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    # discount_amount: 쿠폰의 할인 금액입니다. (예: 5000원)
    discount_amount = db.Column(db.Integer, nullable=False)
    # is_used: 쿠폰을 이미 썼는지 안 썼는지 상태를 표시합니다. (기본값 False: 안 썼음)
    is_used = db.Column(db.Boolean, default=False)
    # user: '쿠폰.user'로 주인을 찾을 수 있게 해줍니다. 한 명이 여러 쿠폰을 가질 수 있습니다. (1:N 관계)
    user = db.relationship('User', backref=db.backref('coupons'))

# =========================================================
# [팀원 1: 이원호님 담당] 상품 전시 및 네비게이션 그룹
# =========================================================

# 4. 상품(Product) 테이블: 쇼핑몰에서 판매하는 전자기기 목록입니다.
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False) # 상품명
    price = db.Column(db.Integer, nullable=False) # 가격
    # category: '스마트폰', '노트북' 등 큰 분류를 적어줍니다. (메뉴바 클릭 시 필터링 용도)
    category = db.Column(db.String(50), nullable=False)
    # brand: '삼성', '애플' 등 브랜드 이름입니다.
    brand = db.Column(db.String(50), nullable=False)
    # stock: 현재 창고에 남은 재고 개수입니다. 결제할 때마다 숫자가 줄어듭니다.
    stock = db.Column(db.Integer, default=100)
    # description: 상품 상세 설명입니다. (nullable=True: 안 적어도 됨)
    description = db.Column(db.Text, nullable=True)
    # image_path: 화면에 띄워줄 상품 사진 파일의 위치(경로)입니다.
    image_path = db.Column(db.String(200), nullable=True)
    # 구성품 이미지 경로 (예: 's26_box.jpg')
    box_image_path = db.Column(db.String(200), nullable=True)
    # 구성품 설명 문구 (예: '1. 스마트폰 | 2. 데이터 케이블...')
    box_description = db.Column(db.Text, nullable=True)
    # 옵션 데이터를 가져오기 위한 연결고리 (1:N 관계)
    options = db.relationship('ProductOption', backref='product', lazy=True)


class ProductOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # product.id와 연결되는 외래키
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    otype = db.Column(db.String(50))  # '용량', '색상', '모델', '칩셋' 등
    oname = db.Column(db.String(100))  # '512GB', '티타늄 블랙' 등 이름
    add_price = db.Column(db.Integer, default=0)  # 기준가에 더할 금액
    image_variant = db.Column(db.String(200))  # 옵션 클릭 시 바뀔 이미지 파일명
    color_code = db.Column(db.String(20))  # 색상 버튼용 HEX 코드 (예: #000000)
# =========================================================
# [팀원 3: 박예인님 담당] 장바구니 및 주문/결제 그룹
# =========================================================
# 5. 장바구니(Cart) 테이블: 고객이 쇼핑하다가 담아둔 물건들입니다.
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # user_id: 회원인 경우 회원 번호가 들어갑니다. (비회원도 장바구니를 쓰기 위해 nullable=True 로 빈칸을 허용합니다)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=True)
    # session_id: 로그인 안 한 비회원이 장바구니를 쓸 때, 브라우저에 임시로 부여하는 식별표입니다.
    session_id = db.Column(db.String(100), nullable=True)
    # product_id: '어떤 상품'을 담았는지 상품 테이블을 연결합니다.
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    # quantity: 몇 개를 담았는지 수량입니다. (기본값 1개)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    # product: 파이썬에서 '장바구니.product.name' 처럼 상품 정보를 쉽게 꺼내오기 위한 끈입니다.
    product = db.relationship('Product')

# 6. 주문(Order) 테이블: 결제가 완료된 영수증 껍데기(메인 정보)입니다.
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # 비회원 주문 허용
    recipient = db.Column(db.String(100), nullable=False) # 택배 받을 사람 이름
    phone = db.Column(db.String(20), nullable=False) # 받을 사람 전화번호
    address = db.Column(db.String(200), nullable=False) # 배송지 주소
    total_price = db.Column(db.Integer, nullable=False) # 총 결제 금액
    payment_method = db.Column(db.String(50), nullable=False) # 결제 수단 (카드, 무통장 등)
    status = db.Column(db.String(50), default='결제완료') # 배송 상태 (결제완료 -> 배송중 -> 배송완료)
    order_date = db.Column(db.DateTime, default=datetime.utcnow) # 주문한 시간
    tracking_number = db.Column(db.String(50), nullable=True) # 운송장 번호 (결제 완료 직후엔 없으므로 빈칸 허용)
    courier_company = db.Column(db.String(50), nullable=True) # 택배사 (예: CJ대한통운, 우체국)
    current_location = db.Column(db.String(100), default='상품 준비 중')
    delivery_message = db.Column(db.String(200), default='주문이 확인되어 배송을 준비하고 있습니다.')
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupon.id'), nullable=True)
    coupon = db.relationship('Coupon', backref='orders')


# 7. 주문 상세(OrderItem) 테이블: 영수증 안에 적힌 구체적인 상품 내역입니다. (한 번 주문에 여러 개를 살 수 있으니까요)
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # order_id: 이 내역이 '몇 번 영수증(Order)'에 속한 것인지 연결합니다.
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete='CASCADE'), nullable=False)
    # product_id: 어떤 물건을 샀는지 연결합니다.
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False) # 산 개수
    # price: 상품 원가가 나중에 변하더라도, '고객이 주문할 당시의 가격'을 기록해두는 공간입니다.
    price = db.Column(db.Integer, nullable=False)
    # order: '상세내역.order'로 부모 영수증 정보를 불러올 수 있습니다.
    order = db.relationship('Order', backref=db.backref('items', cascade='all, delete-orphan'))
    product = db.relationship('Product')
    status = db.Column(db.String(20), nullable=True)

# =========================================================
# [팀원 4: 이강토(본인) 담당] 고객센터 및 리뷰 그룹
# =========================================================

# 8. 리뷰(Review) 테이블: 고객이 작성한 상품평입니다.
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # product_id: 어느 상품에 달린 리뷰인지 연결합니다.
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    # user_id: 누가 쓴 리뷰인지 연결합니다.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False) # 리뷰 내용
    rating = db.Column(db.Integer, default=5) # 별점 (1~5점, 기본 5점)
    image_path = db.Column(db.String(255), nullable=True) # 이미지
    timestamp = db.Column(db.DateTime, default=datetime.utcnow) # 작성 시간
    # product, user: 쉽게 데이터를 꺼내오기 위한 관계 설정입니다.
    product = db.relationship('Product', backref=db.backref('reviews'))
    user = db.relationship('User', backref=db.backref('reviews'))

# 9. FAQ 테이블
class FAQ(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False) # 분류 (예: 배송, 교환/환불, 기기결함)
    question = db.Column(db.String(300), nullable=False) # 질문
    answer = db.Column(db.Text, nullable=False) # 답변


# 같은 이메일로 탈퇴시 마지막 탈퇴 시각만 유지
class WithdrawnEmail(db.Model):
    __tablename__ = "withdrawn_email"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    withdrawn_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))