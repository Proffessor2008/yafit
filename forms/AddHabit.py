from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, IntegerField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired


class AddHabitForm(FlaskForm):
    habit_name = StringField('Название привычки', validators=[DataRequired()])
    duration = IntegerField('Планируемый период соблюдения (дней)', validators=[DataRequired()])
    about_habit = StringField('Описание вашей привычки', validators=[DataRequired()])
    submit = SubmitField('Войти')
