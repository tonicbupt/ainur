# coding: utf-8

from base import db, Base


class BaseImage(Base):

    __tablename__ = 'base_image'

    name = db.Column(db.String(64), unique=True, nullable=False)

    @classmethod
    def create(cls, name):
        b = cls(name=name)
        db.session.add(b)
        db.session.commit()
        return b

    @classmethod
    def list_all(cls):
        return cls.query.order_by(cls.id.desc()).all()
