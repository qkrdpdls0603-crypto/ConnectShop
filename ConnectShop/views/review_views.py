import os
from werkzeug.utils import secure_filename
from flask import Blueprint, request, flash, redirect, url_for, g
from ConnectShop import db
from ConnectShop.models import Review, Order, OrderItem
from datetime import datetime

bp = Blueprint('review', __name__, url_prefix='/review')


def verify_purchase(user_id, product_id):
    purchase_exists = db.session.query(OrderItem).join(Order).filter(
        Order.user_id == user_id,
        OrderItem.product_id == product_id,
        Order.status.in_(['배송완료', '구매확정'])
    ).first()
    return purchase_exists is not None


# 📝 1. 리뷰 작성 (사진 첨부 기능 추가)
@bp.route('/create/<int:product_id>', methods=['POST'])
def create(product_id):
    if g.user is None:
        flash('로그인 후 이용해주세요.')
        return redirect(url_for('auth.login'))

    if not verify_purchase(g.user.id, product_id):
        flash('해당 상품을 구매하고 [배송완료] 또는 [구매확정] 상태인 고객만 리뷰를 작성할 수 있습니다.')
        return redirect(url_for('product.page', product_id=product_id))

        # 🌟 2. 중복 작성 검증 (새로 추가)
    existing_review = Review.query.filter_by(user_id=g.user.id, product_id=product_id).first()
    if existing_review:
        flash('이미 이 상품에 대한 리뷰를 작성하셨습니다. 리뷰는 상품당 1회만 작성 가능합니다.')
        return redirect(url_for('product.page', product_id=product_id))

    content = request.form.get('content')
    rating = request.form.get('rating', type=int)

    # 🌟 이미지 업로드 처리 로직
    image_file = request.files.get('image')
    image_path = None
    if image_file and image_file.filename != '':
        filename = secure_filename(image_file.filename)
        # 폴더가 없으면 자동 생성
        upload_folder = os.path.join('ConnectShop', 'static', 'uploads', 'reviews')
        os.makedirs(upload_folder, exist_ok=True)
        # 파일 저장
        image_file.save(os.path.join(upload_folder, filename))
        image_path = f'uploads/reviews/{filename}'  # DB에 들어갈 경로

    if not content:
        flash('리뷰 내용을 입력해주세요.')
        return redirect(url_for('product.page', product_id=product_id))

    review = Review(
        product_id=product_id,
        user_id=g.user.id,
        content=content,
        rating=rating,
        image_path=image_path,  # 이미지 경로 DB 저장
        timestamp=datetime.utcnow()
    )
    db.session.add(review)
    db.session.commit()

    flash('리뷰가 성공적으로 등록되었습니다. 감사합니다!')
    return redirect(url_for('product.page', product_id=product_id))


# 🗑️ 2. 리뷰 삭제
@bp.route('/delete/<int:review_id>', methods=['POST'])
def delete(review_id):
    review = Review.query.get_or_404(review_id)
    product_id = review.product_id

    # 🌟 본인 검증
    if not g.user or g.user.id != review.user_id:
        flash('삭제 권한이 없습니다.')
        return redirect(url_for('product.page', product_id=product_id))

    db.session.delete(review)
    db.session.commit()
    flash('리뷰가 정상적으로 삭제되었습니다.')
    return redirect(url_for('product.page', product_id=product_id))


# ✏️ 3. 리뷰 수정
@bp.route('/edit/<int:review_id>', methods=['POST'])
def edit(review_id):
    review = Review.query.get_or_404(review_id)
    product_id = review.product_id

    # 🌟 본인 검증
    if not g.user or g.user.id != review.user_id:
        flash('수정 권한이 없습니다.')
        return redirect(url_for('product.page', product_id=product_id))

    review.content = request.form.get('content')
    review.rating = request.form.get('rating', type=int)

    # 이미지를 새로 올렸다면 덮어쓰기
    image_file = request.files.get('image')
    if image_file and image_file.filename != '':
        filename = secure_filename(image_file.filename)
        upload_folder = os.path.join('ConnectShop', 'static', 'uploads', 'reviews')
        os.makedirs(upload_folder, exist_ok=True)
        image_file.save(os.path.join(upload_folder, filename))
        review.image_path = f'uploads/reviews/{filename}'

    db.session.commit()
    flash('리뷰가 성공적으로 수정되었습니다.')
    return redirect(url_for('product.page', product_id=product_id))