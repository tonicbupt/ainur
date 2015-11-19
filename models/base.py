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
    def get(cls, id):
        return cls.query.get(id)

    @classmethod
    def get_multi(cls, ids):
        return filter(None, [cls.get(i) for i in ids])

    @classmethod
    def delete_by_id(cls, oid):
        cls.query.filter_by(id=oid).delete()
        db.session.commit()

    @classmethod
    def list(cls, skip, limit, order_by=None):
        q = cls.query
        if order_by is not None:
            q = q.order_by(order_by)
        return q.offset(skip).limit(limit).all()
