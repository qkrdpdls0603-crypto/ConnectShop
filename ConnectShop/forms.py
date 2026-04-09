import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError




class UserCreateForm(FlaskForm):
    username = StringField('이름', validators=[DataRequired('이름은 필수 입력 항목입니다.'), Length(min=3, max=25)])
    password1 = PasswordField('비밀번호', validators=[DataRequired('비밀번호'), EqualTo('password2', message='비밀번호가 일치하지 않습니다.')])
    password2 = PasswordField('비밀번호확인', validators=[DataRequired('비밀번호와 똑같이 입력하세요')])
    email = EmailField('이메일', validators=[DataRequired('이메일은 필수 입력 항목입니다.'), Email('올바른 이메일 형식이 아닙니다.')])
    phone = StringField("Phone")

    def validate_phone(self, field):
        field.data = re.sub(r'\D', '', field.data or "")
        if not re.fullmatch(r'010\d{8}', field.data):
            raise ValidationError('010으로 시작하는 11자리 핸드폰 번호를 입력하세요. (예: 01012345678)')



class UserLoginForm(FlaskForm):
    email = EmailField('이메일', validators=[DataRequired('이메일은 필수 입력 항목입니다.'), Email('올바른 이메일 형식이 아닙니다.')])
    password = PasswordField('비밀번호', validators=[DataRequired('비밀번호은 필수 입력 항목입니다.')])


class FindIdForm(FlaskForm):
    username = StringField('이름', validators=[DataRequired('가입하신 이름을 입력해주세요.')])

class ResetPasswordForm(FlaskForm):
    # 비밀번호 재설정을 위해 아이디와 이메일 확인이 필요합니다.
    username = StringField('이름', validators=[DataRequired('이름를 입력해주세요.')])
    email = EmailField('이메일', validators=[DataRequired('이메일을 입력해주세요.'), Email()])
    password1 = PasswordField('새 비밀번호', validators=[
        DataRequired('새 비밀번호를 입력하세요.'),
        EqualTo('password2', message='비밀번호가 일치하지 않습니다.')
    ])
    password2 = PasswordField('새 비밀번호 확인', validators=[DataRequired('비밀번호를 한 번 더 입력하세요.')])