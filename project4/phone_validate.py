import phonenumbers
from wtforms import ValidationError


def phone_validate(form, phone_field):
    try:
        phone = phonenumbers.parse(phone_field.data, region='RU')
        phone_field.data = phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        raise ValidationError('Введите номер телефона в формате 11 цифр, например +79001234567')
