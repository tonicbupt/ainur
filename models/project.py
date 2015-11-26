# coding: utf-8

import sqlalchemy.exc

from libs.clients import eru
from models.base import db, Base


class Project(object):

    def __init__(self, id, git, name, update, group_id, _user_id):
        self.id = id
        self.git = git
        self.name = name
        self.update = update
        self.group_id = group_id
        self._user_id = _user_id

    @classmethod
    def get_by_name(cls, name):
        try:
            p = eru.get_app(name)
            return p and cls(**p) or None
        except:
            return None

    @classmethod
    def get_multi_by_name(cls, names):
        return filter(None, [cls.get_by_name(n) for n in names])

    def get_accessible_users(self):
        from .user import User
        user_id = ProjectUserMapping.get_user_id_by_name(self.name)
        return User.get_multi(user_id)

    def is_accessible(self, user):
        return user and (user.is_admin() or user.is_lb_mgr() or user in self.get_accessible_users())


class ProjectUserMapping(Base):

    __tablename__ = 'project_user_mapping'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'name'),
    )

    name = db.Column(db.String(255), nullable=False, index=True, default='')
    user_id = db.Column(db.Integer, nullable=False, default=0)

    @classmethod
    def add(cls, name, user_id):
        try:
            mapping = cls(name=name, user_id=user_id)
            db.session.add(mapping)
            db.session.commit()
            return mapping
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
            return None

    @classmethod
    def delete(cls, name, user_id):
        cls.query.filter_by(user_id=user_id, name=name).delete()
        db.session.commit()

    @classmethod
    def get_user_id_by_name(cls, name, start=0, limit=20):
        rs = cls.query.filter_by(name=name)
        return [r.user_id for r in rs[start:start+limit] if r]

    @classmethod
    def get_name_by_user_id(cls, user_id, start=0, limit=20):
        rs = cls.query.filter_by(user_id=user_id)
        return [r.name for r in rs[start:start+limit] if r]
