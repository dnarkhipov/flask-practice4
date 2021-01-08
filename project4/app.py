import os
import json
import random

from base64 import urlsafe_b64encode, urlsafe_b64decode

from flask import Flask, render_template, send_from_directory, redirect, url_for, request
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from sqlalchemy.exc import DBAPIError

from .booking_form import BookingForm
from .request_form import RequestForm
from .sort_mode_form import SortModeForm
from .database import db
from .models import Goal, Teacher, SearchRequest, BookingRequest


weekday_names_ru = {
    "mon": {"short": "Пн", "full": "Понедельник"},
    "tue": {"short": "Вт", "full": "Вторник"},
    "wed": {"short": "Ср", "full": "Среда"},
    "thu": {"short": "Чт", "full": "Четверг"},
    "fri": {"short": "Пт", "full": "Пятница"},
    "sat": {"short": "Сб", "full": "Суббота"},
    "sun": {"short": "Вс", "full": "Воскресенье"}
}


request_time_limits = {
    'limit1_2': '1-2 часа в неделю',
    'limit3_5': '3-5 часов в неделю',
    'limit5_7': '5-7 часов в неделю',
    'limit7_10': '7-10 часов в неделю'
}

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = '1a0b329d-f511-47d0-a111-335d2acbfd88'   # SECRET_KEY

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./data/project4.db'
db.init_app(app)
migrate = Migrate(app, db)


base_template_attr = {
    # Базовые настроки макета (название сайта, пунктов меню и т.п.)
    "title": "TINYSTEPS",
    "nav_title": "TINYSTEPS",
    "nav_items": {
        "/all/": "Все репетиторы",
        "/request/": "Заявка на подбор",
    }
}


@app.route('/')
def main():
    goals = db.session.query(Goal).order_by(Goal.id).all()
    teachers = db.session.query(Teacher).all()
    return render_template(
        'index.html',
        **base_template_attr,
        goals=goals,
        teachers=random.sample(teachers, 6)
    )


@app.route('/all/', methods=['get', 'post'])
def get_all():
    goals = db.session.query(Goal).order_by(Goal.id).all()

    sort_form = SortModeForm()
    mode = sort_form.sort_mode.data
    if mode == 'random':
        teachers = db.session.query(Teacher).all()
        random.shuffle(teachers)
    elif mode == 'rating_desc':
        teachers = db.session.query(Teacher).order_by(Teacher.rating.desc()).all()
    elif mode == 'price_desc':
        teachers = db.session.query(Teacher).order_by(Teacher.price.desc()).all()
    elif mode == 'price_asc':
        teachers = db.session.query(Teacher).order_by(Teacher.price).all()
    else:
        teachers = db.session.query(Teacher).order_by(Teacher.id).all()

    return render_template(
        'all.html',
        **base_template_attr,
        goals=goals,
        teachers=teachers,
        form=sort_form
    )


@app.route('/goals/<goal>/')
def get_goal(goal):
    goal_rec = db.session.query(Goal).filter(Goal.name == goal).first()
    if goal_rec is None:
        return redirect('/all')
    teachers = db.session.query(Teacher).filter(Teacher.goals.any(Goal.name == goal)).order_by(Teacher.rating.desc()).all()
    return render_template(
        'goal.html',
        **base_template_attr,
        goal=goal_rec,
        teachers=teachers
    )


@app.route('/profiles/<int:profile_id>/')
def get_profile_by_id(profile_id: int):
    # по условиям задания: Когда преподавателя не существует, выбросьте 404.
    teacher = db.session.query(Teacher).get_or_404(profile_id)
    # if not teacher:
    #     return redirect('/all')

    return render_template(
        'profile.html',
        **base_template_attr,
        profile=teacher,
        weekday_names=weekday_names_ru
    )


@app.route('/request/', methods=['GET', 'POST'])
def get_request():
    goals = db.session.query(Goal).order_by(Goal.id).all()

    form = RequestForm()
    form.goal_id.choices = [(goal.id, goal.description_ru) for goal in goals]
    form.time_limit.choices = [(k, v) for k, v in request_time_limits.items()]

    if request.method == 'POST':
        if form.validate():
            request_record = SearchRequest()
            form.populate_obj(request_record)
            try:
                db.session.add(request_record)
                db.session.commit()
            except DBAPIError as err:
                return f'Internal DBAPI error: {err}', 500

            # пакуем данные формы для передачи в квитанцию
            fdata = urlsafe_b64encode(bytes(json.dumps(request_record.as_dict(), ensure_ascii=False), 'utf-8'))
            return redirect(url_for('get_request_done', fdata=fdata))
    else:
        form.goal_id.default = next(iter(goal.id for goal in goals), 'empty')
        form.time_limit.default = next(iter(request_time_limits), 'empty')
        form.process()

    return render_template(
        'request.html',
        **base_template_attr,
        form=form
    )


@app.route('/request_done/<fdata>')
def get_request_done(fdata):
    # распаковываем данные формы
    request_record = json.loads(urlsafe_b64decode(fdata).decode('utf-8'))
    goal_rec = db.session.query(Goal).get(request_record['goal_id'])
    return render_template(
        'request_done.html',
        **base_template_attr,
        request_info=request_record,
        goal=goal_rec.description_ru,
        time_limit=request_time_limits[request_record['time_limit']]
    )


@app.route('/booking/<int:profile_id>/<day_of_week>/<time>/', methods=['GET', 'POST'])
def get_booking_form(profile_id: int, day_of_week, time):
    teacher = db.session.query(Teacher).get_or_404(profile_id)
    # if not teacher:
    #     return redirect('/all')

    form = BookingForm()
    form.teacher_id.data = profile_id
    form.client_weekday.data = day_of_week
    form.client_time.data = f'{time[:2]}:{time[-2:]}'

    if request.method == 'POST' and form.validate():
        booking_record = BookingRequest()
        form.populate_obj(booking_record)
        try:
            db.session.add(booking_record)
            db.session.commit()
        except DBAPIError as err:
            return f'Internal DBAPI error: {err}', 500

        # пакуем данные формы для передачи в квитанцию
        fdata = urlsafe_b64encode(bytes(json.dumps(booking_record.as_dict(), ensure_ascii=False), 'utf-8'))
        return redirect(url_for('get_booking_form_done', fdata=fdata))

    return render_template(
        'booking.html',
        **base_template_attr,
        profile=teacher,
        form=form,
        weekday_name=weekday_names_ru[day_of_week]['full']
    )


@app.route('/booking_done/<fdata>')
def get_booking_form_done(fdata):
    # распаковываем данные формы
    booking_record = json.loads(urlsafe_b64decode(fdata).decode('utf-8'))
    return render_template(
        'booking_done.html',
        **base_template_attr,
        booking_info=booking_record,
        weekday_name=weekday_names_ru[booking_record['client_weekday']]['full']
    )


# https://flask.palletsprojects.com/en/1.1.x/patterns/favicon/
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run()
