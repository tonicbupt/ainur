# coding: utf-8

from datetime import datetime
from models.base import db, Base, PropsMixin, PropsItem
from models.consts import OPLOG_KIND_MAPPING


class OPLog(Base, PropsMixin):

    __tablename__ = 'oplog'
    __table_args__ = (
        db.Index('user_kind', 'user_id', 'kind'),
    )

    user_id = db.Column(db.Integer, index=True)
    time = db.Column(db.DateTime, default=datetime.now)
    kind = db.Column(db.Integer, index=True)
    action = db.Column(db.Integer, index=True)

    project_name = PropsItem('project_name')
    container_id = PropsItem('container_id')
    balancer_id = PropsItem('balancer_id')
    image = PropsItem('image')
    privilege = PropsItem('privilege')
    acceptor = PropsItem('acceptor')
    record_id = PropsItem('record_id')
    data = PropsItem('data')

    def get_uuid(self):
        return '/ainur/oplog/%s' % self.id

    @classmethod
    def create(cls, user_id, action):
        kind = OPLOG_KIND_MAPPING.get(action, None)
        if kind is None:
            return None

        log = cls(user_id=user_id, kind=kind, action=action)
        db.session.add(log)
        db.session.commit()
        return log

    @classmethod
    def get_by_user_id(cls, user_id, kind=None, time=None, action=None, start=0, limit=20):
        q = cls.query.filter_by(user_id=user_id)
        if kind is not None:
            q = q.filter_by(kind=kind)
        if time is not None:
            q = q.filter_by(time=time)
        if action is not None:
            q = q.filter_by(action=action)
        q = q.order_by(cls.id.desc())
        return q[start:start+limit]

    @property
    def user(self):
        from .user import User
        return User.get(self.user_id)

    @property
    def description(self):
        return ''
