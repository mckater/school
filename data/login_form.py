import sqlalchemy
from flask_login import UserMixin

from .db_session import SqlAlchemyBase


class MainClassTable(SqlAlchemyBase, UserMixin):
    __tablename__ = 'myclass'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    log = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    score = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    # hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def __repr__(self):
        return f'<Р.М.> {self.id} - {self.log}'

    # def set_password(self, password):
    #     self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return password == self.password
        # return check_password_hash(self.hashed_password, password)
