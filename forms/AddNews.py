from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, IntegerField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired


class AddNewsForm(FlaskForm):
    news_name = StringField('Заголовок новости', validators=[DataRequired()])
    news_content = StringField('Содержание новости', validators=[DataRequired()])
    submit = SubmitField('Опубликовать')