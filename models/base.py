from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    db.init_app(app)
    db.app = app
    db.create_all()


class Base(db.Model):
    __abstract__ = True
    __table_args__ = {'mysql_charset': 'utf8'}

    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def delete(cls, oid):
        db.session.delete(cls.query.get(oid))
        db.session.commit()

    @classmethod
    def list(cls, skip, limit):
        return cls.query.offset(skip).limit(limit).all()
