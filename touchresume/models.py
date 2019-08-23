from uuid import uuid4
from functools import partial
from datetime import datetime

from flask_login import UserMixin

from . import db, login, ma


db.RequiredColumn = partial(db.Column, nullable=False)


class User(db.Model, UserMixin):

    __tablename__ = 'users'

    identity = db.RequiredColumn(
        db.String(120), primary_key=True, unique=True,
        index=True, default=lambda: f'{uuid4()}')

    accounts = db.relationship(
        'Account', back_populates='user', cascade='all,delete')

    def get_id(self):
        return self.identity

    def __str__(self):
        return self.get_id()


class Account(db.Model):

    __tablename__ = 'accounts'

    identity = db.RequiredColumn(
        db.String(120), primary_key=True, unique=True, index=True)
    access = db.RequiredColumn(db.String(200))
    refresh = db.RequiredColumn(db.String(200))
    expires = db.RequiredColumn(db.DateTime)
    provider = db.RequiredColumn(db.String(120))

    user_id = db.RequiredColumn(
        db.String(120), db.ForeignKey('users.identity', ondelete='CASCADE'))
    user = db.relationship('User', back_populates='accounts')

    resume = db.relationship(
        'Resume', back_populates='account', cascade='all,delete,delete-orphan')

    def __str__(self):
        return f'{self.identity}, provider={self.provider}, user={self.user}'


class Resume(db.Model):

    __tablename__ = 'resume'

    identity = db.RequiredColumn(
        db.String(120), primary_key=True, unique=True, index=True)
    published = db.RequiredColumn(db.DateTime, default=datetime.utcnow)
    autoupdate = db.RequiredColumn(db.Boolean, default=False)

    account_id = db.RequiredColumn(
        db.String(120), db.ForeignKey('accounts.identity', ondelete='CASCADE'))
    account = db.relationship('Account', back_populates='resume')

    @property
    def updelta(self):
        return (datetime.utcnow() - self.published)

    def __str__(self):
        return (
            f'{self.identity}, autoupdate={self.autoupdate}, '
            f'account={self.account.identity}, user={self.account.user}, '
            f'published={self.published}, updelta={self.updelta}')


class Task(db.Model):

    __tablename__ = 'tasks'

    identity = db.RequiredColumn(
        db.String(120), primary_key=True, unique=True,
        index=True, default=lambda: f'{uuid4()}')
    name = db.RequiredColumn(db.String(120))
    started_at = db.RequiredColumn(db.DateTime)
    finished_at = db.RequiredColumn(db.DateTime)
    success = db.RequiredColumn(db.Integer)
    skipped = db.RequiredColumn(db.Integer)
    total = db.RequiredColumn(db.Integer)

    @property
    def duration(self):
        return (self.finished_at - self.started_at).total_seconds()

    def __str__(self):
        return f'{self.identity}, {self.name}'


class ResumeSchema(ma.ModelSchema):
    class Meta:
        model = Resume
        unknown = 'INCLUDE'


@login.user_loader
def load_user(user_id):
    try:
        return User.query.get(user_id)
    except Exception:  # pragma: no cover
        return None
