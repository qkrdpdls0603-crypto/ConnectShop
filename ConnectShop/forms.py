import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError, Optional, Regexp


class UserCreateForm(FlaskForm):
    username = StringField('이름', validators=[DataRequired('이름은 필수 입력 항목입니다.'), Length(min=3, max=25)])
    password1 = PasswordField('비밀번호', validators=[DataRequired('비밀번호는 필수 입력 항목입니다.'), EqualTo('password2', message='비밀번호가 일치하지 않습니다.')])
    password2 = PasswordField('비밀번호확인', validators=[DataRequired('비밀번호 확인은 필수입니다.')])
    email = EmailField('이메일', validators=[DataRequired('이메일은 필수입니다.'), Email('올바른 이메일 형식이 아닙니다.')])
    phone = StringField("핸드폰 번호", validators=[DataRequired('핸드폰 번호는 필수 입력 항목입니다.')])

    def validate_phone(self, field):
        cleaned = re.sub(r'\D', '', field.data or "")
        field.data = cleaned
        if not re.fullmatch(r'010\d{8}', cleaned):
            raise ValidationError('010으로 시작하는 11자리 핸드폰 번호를 입력하세요.')


class UserLoginForm(FlaskForm):
    email = EmailField('이메일', validators=[DataRequired('이메일을 입력하세요.'), Email()])
    password = PasswordField('비밀번호', validators=[DataRequired('비밀번호를 입력하세요.')])


class FindIdForm(FlaskForm):
    username = StringField('이름', validators=[DataRequired('가입하신 이름을 입력해주세요.')])

    phone = StringField(
        '휴대폰 번호',
        validators=[
            DataRequired(message="휴대폰 번호를 입력하세요."),
            Regexp(r'^\d{10,11}$', message="숫자만 10~11자리로 입력하세요."),
            Length(min=10, max=11)
        ],
        render_kw={"placeholder": "숫자만 입력하세요 (예: 01012345678)"}
    )
    submit = SubmitField("아이디 찾기")


class ResetPasswordForm(FlaskForm):
    username = StringField('이름', validators=[DataRequired('이름을 입력하세요.')])
    email = EmailField('이메일', validators=[DataRequired('이메일을 입력하세요.'), Email()])
    password1 = PasswordField('새 비밀번호', validators=[DataRequired(), EqualTo('password2', message='비밀번호가 일치하지 않습니다.')])
    password2 = PasswordField('새 비밀번호 확인', validators=[DataRequired()])


class UserUpdateForm(FlaskForm):
    username = StringField('이름', validators=[DataRequired('이름은 필수 입력 항목입니다.'), Length(min=3, max=25)])
    email = EmailField('이메일', validators=[DataRequired('이메일은 필수입니다.'), Email('올바른 이메일 형식이 아닙니다.')])
    phone = StringField("핸드폰 번호", validators=[DataRequired('핸드폰 번호는 필수 입력 항목입니다.')])

    password1 = PasswordField('새 비밀번호', validators=[Optional(), EqualTo('password2', message='비밀번호가 일치하지 않습니다.')])
    password2 = PasswordField('새 비밀번호 확인', validators=[Optional()])

    def validate_phone(self, field):
        cleaned = re.sub(r'\D', '', field.data or "")
        field.data = cleaned
        if not re.fullmatch(r'010\d{8}', cleaned):
            raise ValidationError('010으로 시작하는 11자리 핸드폰 번호를 입력하세요.')
