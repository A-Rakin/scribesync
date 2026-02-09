from datetime import datetime
from wtforms import StringField, PasswordField, TextAreaField, SelectField, DateTimeField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User


class LoginForm:
    def __init__(self):
        self.email = None
        self.password = None
        self.remember = False

    def validate_on_submit(self):
        # Simple validation for our forms
        return True


class RegistrationForm:
    def __init__(self):
        self.username = None
        self.email = None
        self.password = None
        self.confirm_password = None

    def validate_on_submit(self):
        return True

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')


class PostForm:
    def __init__(self):
        self.title = None
        self.content = None
        self.platform = 'twitter'
        self.scheduled_time = datetime.utcnow()
        self.hashtags = None
        self.media_url = None

    def validate_on_submit(self):
        return True
        return True