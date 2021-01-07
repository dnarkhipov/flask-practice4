from .database import db, Model, Column


teacher_goals = db.Table(
    'teacher_goals',
    Column('goal_id', db.Integer, db.ForeignKey('goals.id')),
    Column('teacher_id', db.Integer, db.ForeignKey('teachers.id'))
)


class Goal(Model):
    __tablename__ = 'goals'
    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(80), nullable=False)
    description_ru = Column(db.String(80), nullable=False)
    teachers = db.relationship(
        'Teacher',
        secondary=teacher_goals,
        back_populates='goals'
    )


class Teacher(Model):
    __tablename__ = 'teachers'
    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(120), nullable=False)
    about = Column(db.Text, nullable=False)
    rating = Column(db.Float, nullable=False)
    picture = Column(db.String(200), nullable=False)
    price = Column(db.Integer, nullable=False)
    goals = db.relationship(
        'Goal',
        secondary=teacher_goals,
        back_populates='teachers'
    )
    free = Column(db.String(500), nullable=False)


class BookingRequest(Model):
    __tablename__ = 'booking_requests'
    id = Column(db.Integer, primary_key=True)
    client_weekday = Column(db.String(80), nullable=False)
    client_time = Column(db.String(5), nullable=False)
    teacher_id = Column(db.Integer, db.ForeignKey('teachers.id'))
    client_name = Column(db.String(80), nullable=False)
    client_phone= Column(db.String(50), nullable=False)


class SearchRequest(Model):
    __tablename__ = 'search_requests'
    id = Column(db.Integer, primary_key=True)
    goal_id = Column(db.Integer, db.ForeignKey('goals.id'))
    time_limit = Column(db.String(30), nullable=False)
    client_name = Column(db.String(80), nullable=False)
    client_phone= Column(db.String(50), nullable=False)
