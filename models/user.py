# coding: utf-8

from models.base import db, Base
from models.consts import USER_ROLE


class User(Base):

    __tablename__ = 'user'

    uid = db.Column(db.String(64), unique=True, nullable=False)
    group = db.Column(db.String(64))
    realname = db.Column(db.String(64), index=True, nullable=False)
    priv_flags = db.Column(db.Integer, nullable=False, default=USER_ROLE.user)

    def __hash__(self):
        return self.id

    @classmethod
    def get_or_create(cls, uid, realname):
        u = cls.get_by_uid(uid)
        if u:
            return u
        u = cls(uid=uid, realname=realname)
        db.session.add(u)
        db.session.commit()
        return u

    @classmethod
    def get_by_uid(cls, uid):
        return cls.query.filter_by(uid=uid).first()

    @classmethod
    def get_all(cls, start=0, limit=20):
        q = cls.query.order_by(cls.uid.desc())
        return q[start:start+limit]

    def set_group(self, group):
        self.group = group
        db.session.add(self)
        db.session.commit()

    def set_privilege(self, privilege):
        self.priv_flags = privilege
        db.session.add(self)
        db.session.commit()

    def get_accessible_projects(self, start=0, limit=20):
        from .project import ProjectUserMapping, Project
        names = ProjectUserMapping.get_name_by_user_id(self.id, start, limit)
        return Project.get_multi_by_name(names)

    def grant_project(self, name):
        from .project import ProjectUserMapping
        ProjectUserMapping.add(name, self.id)

    def is_admin(self):
        return self.priv_flags & USER_ROLE.admin

    def is_lb_mgr(self):
        return self.priv_flags & USER_ROLE.lb
