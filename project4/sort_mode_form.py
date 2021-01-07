from flask_wtf import FlaskForm
from wtforms import SelectField


class SortModeForm(FlaskForm):
    sort_mode = SelectField(
        'сортировать',
        choices=[
            ('random', 'В случайном порядке'),
            ('rating_desc', 'Сначала лучшие по рейтингу'),
            ('price_desc', 'Сначала дорогие'),
            ('price_asc', 'Сначала недорогие')
        ],
        default='random'
    )
