"""Добавлена новая цель Для программирования

Revision ID: b3999d67d0db
Revises: d973b17b4626
Create Date: 2021-01-08 00:53:51.639283

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm
from project4.models import Goal, Teacher


# revision identifiers, used by Alembic.
revision = 'b3999d67d0db'
down_revision = 'd973b17b4626'
branch_labels = None
depends_on = None


def upgrade():
    # https://stackoverflow.com/questions/24612395/how-do-i-execute-inserts-and-updates-in-an-alembic-upgrade-script
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    # – добавьте новую цель "для программирования" преподавателям   8,9,10,11
    goal = Goal(name='dev', description_ru='Для программирования')
    session.add(goal)

    teachers = session.query(Teacher).filter(Teacher.id.in_([8, 9, 10, 11])).all()
    for teacher in teachers:
        teacher.goals.append(goal)

    session.commit()


def downgrade():
    pass
