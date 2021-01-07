from flask_wtf import FlaskForm
from wtforms import RadioField, StringField
from wtforms import validators
from wtforms.fields.html5 import TelField

from .phone_validate import phone_validate


class RequestForm(FlaskForm):
    goal = RadioField('Какая цель занятий?', [validators.InputRequired()])
    time_limit = RadioField('Сколько времени есть?', [validators.InputRequired()])

    client_name = StringField('Вас зовут', [validators.InputRequired()])
    client_phone = TelField('Ваш телефон', [validators.InputRequired(), phone_validate])
