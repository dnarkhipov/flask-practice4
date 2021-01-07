from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField
from wtforms import validators
from wtforms.fields.html5 import TelField

from .phone_validate import phone_validate


class BookingForm(FlaskForm):
    client_weekday = HiddenField()
    client_time = HiddenField()
    client_teacher = HiddenField()

    client_name = StringField('Вас зовут', [validators.InputRequired()])
    client_phone = TelField('Ваш телефон', [validators.InputRequired(), phone_validate])
