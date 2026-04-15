from ConnectShop import create_app, db
from ConnectShop.models import FAQ

app = create_app()

# 플라스크 앱 환경 안에서 DB 작업을 수행하도록 설정
with app.app_context():
    # 기존 데이터가 있으면 싹 지우고 (중복 방지)
    FAQ.query.delete()

    f1 = FAQ(category='배송', question='배송은 얼마나 걸리나요?', answer='결제 완료 후 영업일 기준 1~3일 이내에 출고됩니다.')
    f2 = FAQ(category='환불', question='반품 신청은 어떻게 하나요?', answer='마이페이지 > 주문내역에서 수령 후 7일 이내에 신청 가능합니다.')
    f3 = FAQ(category='계정', question='비밀번호를 잊어버렸어요.', answer='로그인 화면 하단의 [비밀번호 찾기]를 이용해 주세요.')

    f4 = FAQ(
        category='배송',
        question='주문/배송 상태는 어디에서 확인하나요?',
        answer='주문/배송 상태는 페이지 우측 상단의 사람 모양 아이콘에서 주문/배송조회에서 확인할 수 있습니다.<br>비회원 주문/배송조회도 우측 상단의 사람 모양 아이콘에서 이용하실 수 있습니다.'
    )

    # 리스트 안에 f4까지 꼭 포함해서 한 번에 저장합니다.
    db.session.add_all([f1, f2, f3, f4])
    db.session.commit()

    print("✅ FAQ 더미 데이터 4개가 성공적으로 생성되었습니다!")