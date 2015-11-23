# coding: utf-8

import json
from libs.ext import db, rds

class Base(db.Model):
    __abstract__ = True
    __table_args__ = {'mysql_charset': 'utf8'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

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

    def to_dict(self):
        return {}


class PropsMixin(object):
    """丢redis里"""

    def get_uuid(self):
        raise NotImplementedError('Need uuid to idenify objects')

    @property
    def _property_key(self):
        return self.get_uuid() + '/property'

    def get_props(self):
        props = rds.get(self._property_key) or '{}'
        return json.loads(props)

    def set_props(self, props):
        rds.set(self._property_key, json.dumps(props))

    def destroy_props(self):
        rds.delete(self._property_key)

    props = property(get_props, set_props, destroy_props)

    def update_props(self, **kw):
        props = self.props
        props.update(kw)
        self.props = props

    def get_props_item(self, key, default=None):
        return self.props.get(key, default)

    def set_props_item(self, key, value):
        props = self.props
        props[key] = value
        self.props = props

    def delete_props_item(self, key):
        props = self.props
        props.pop(key, None)
        self.props = props


class PropsItem(object):

    def __init__(self, name, default=None, type=None):
        self.name = name
        self.default = default
        self.type = type

    def __get__(self, obj, obj_type):
        r = obj.get_props_item(self.name, self.default)
        if self.type:
            r = self.type(r)
        return r

    def __set__(self, obj, value):
        obj.set_props_item(self.name, value)

    def __delete__(self, obj):
        obj.delete_props_item(self.name)
