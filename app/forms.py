from wtforms.form import Form
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, ValidationError
from database import User
import logging

logger = logging.getLogger(__name__)


class MyForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    @staticmethod
    def validate_username(field):
        logger.info(f"Checking if username '{field.data}' already exists...")
        if User.get_or_none(User.username == field.data):
            logger.warning(f"Username '{field.data}' is already taken.")
            raise ValidationError('That username is taken. Please choose a different one.')

    @staticmethod
    def validate_email(field):
        logger.info(f"Checking if email '{field.data}' already exists...")
        if User.get_or_none(User.email == field.data):
            logger.warning(f"Email '{field.data}' is already taken.")
            raise ValidationError('That email is taken. Please choose a different one.')
