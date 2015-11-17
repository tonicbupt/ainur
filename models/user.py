# coding: utf-8

from base import db, Base

PRIV_USER = 1
PRIV_ADMIN = PRIV_USER << 1
PRIV_LB = PRIV_ADMIN << 1


class User(Base):
    __tablename__ = 'user'

    uid = db.Column(db.String(64), unique=True, nullable=False)
    group = db.Column(db.String(64))
    realname = db.Column(db.String(64), index=True, nullable=False)
    priv_flags = db.Column(db.Integer, nullable=False, default=PRIV_USER)

    @staticmethod
    def get_by_uid(uid):
        return User.query.filter_by(uid=uid).first()

    def is_admin(self):
        return self.priv_flags & PRIV_ADMIN

    def is_lb_mgr(self):
        return self.priv_flags & PRIV_LB
