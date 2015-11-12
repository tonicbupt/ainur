from werkzeug.utils import cached_property

from base import db, Base

PRIV_USER = 1
PRIV_ADMIN = PRIV_USER << 1
PRIV_LB = PRIV_ADMIN << 1


class User(Base):
    __tablename__ = 'user'

    uid = db.Column(db.String(64), unique=True, nullable=False)
    realname = db.Column(db.Unicode(64), index=True, nullable=False)
    group = db.Column(db.String(64))
    priv_flags = db.Column(db.Integer, nullable=False, default=lambda: 0)

    @staticmethod
    def get_by_uid(uid):
        return User.query.filter_by(uid=uid).first()

    @cached_property
    def active(self):
        return self.priv_flags & PRIV_USER != 0

    @cached_property
    def is_admin(self):
        return self.priv_flags & PRIV_ADMIN != 0

    @cached_property
    def is_lb_mgr(self):
        return self.priv_flags & PRIV_LB != 0
