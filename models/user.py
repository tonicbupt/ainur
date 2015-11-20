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

    def get_accessible_projects(self, start=0, limit=20):
        from .project import ProjectUserMapping, Project
        names = ProjectUserMapping.get_name_by_user_id(self.id, start, limit)
        return Project.get_multi_by_name(names)

    def grant_project(self, name):
        from .project import ProjectUserMapping
        ProjectUserMapping.add(name, self.id)

    def is_admin(self):
        return self.priv_flags & PRIV_ADMIN

    def is_lb_mgr(self):
        return self.priv_flags & PRIV_LB
