# coding: utf-8

import json
import requests

from base import db, Base
from clients import eru


class BalanceRecord(Base):

    __tablename__ = 'balancer_record'

    appname = db.Column(db.String(255), index=True)
    entrypoint = db.Column(db.String(255), index=True)
    domain = db.Column(db.String(255))
    balancer_id = db.Column(db.Integer, index=True)

    @classmethod
    def create(cls, appname, entrypoint, domain, balancer_id):
        r = cls(appname=appname, entrypoint=entrypoint, domain=domain, balancer_id=balancer_id)
        db.session.add(r)
        db.session.commit()

        add_record_rules(r)
        return r

    @classmethod
    def get_by_balancer_id(cls, balancer_id):
        return cls.query.filter_by(balancer_id=balancer_id).order_by(cls.id.desc()).all()

    @classmethod
    def delete_by_balancer_id(cls, balancer_id):
        cls.query.filter_by(balancer_id=balancer_id).delete()
        db.session.commit()

    @property
    def backend_name(self):
        return '%s_%s' % (self.appname, self.entrypoint)

    @property
    def balancer(self):
        return Balancer.get(self.balancer_id)

    def get_backends(self):
        backends = []
        containers = eru.list_app_containers(self.appname, limit=100)
        for container in containers['containers']:
            if container['entrypoint'] != self.entrypoint:
                continue
            backends.extend(container['backends'])
        return backends

    def delete(self):
        delete_record_rules(self)
        db.session.delete(self)
        db.session.commit()


class Balancer(Base):

    __tablename__ = 'balancer'

    addr = db.Column(db.String(255), nullable=False)
    group = db.Column(db.String(255), nullable=False, index=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    container_id = db.Column(db.String(64), nullable=False, index=True)

    def __init__(self, addr, group, user_id, container_id):
        self.addr = addr
        self.group = group
        self.user_id = user_id
        self.container_id = container_id

    @classmethod
    def create(cls, addr, group, user_id, container_id):
        b = cls(addr, group, user_id, container_id)
        db.session.add(b)
        db.session.commit()
        return b

    @classmethod
    def get_by_group(cls, group):
        return cls.query.filter_by(group=group).order_by(cls.id.desc()).all()

    @classmethod
    def get_by_user(cls, user_id):
        return cls.query.filter_by(user_id=user_id).order_by(cls.id.desc()).all()

    @property
    def name(self):
        return self.container_id

    def add_record(self, appname, entrypoint, domain):
        """
        意思是说把这个appname的应用的entrypoint下面的所有后端,
        都路由给domain这个域名
        """
        return BalanceRecord.create(appname, entrypoint, domain, self.id)

    def get_records(self):
        return BalanceRecord.get_by_balancer_id(self.id)

    def delete(self):
        BalanceRecord.delete_by_balancer_id(self.id)
        db.session.delete(self)
        db.session.commit()


class LBClient(object):

    def __init__(self, addr):
        if not addr.startswith('http://'):
            addr = 'http://%s' % addr
        self.addr = addr

    def _get(self, url):
        resp = requests.get(url)
        return resp.status_code == 200 and resp.json() or None

    def _put(self, url, data):
        resp = requests.put(url, data=json.dumps(data))
        return resp.status_code == 200

    def _delete(self, url, data):
        resp = requests.delete(url, data=json.dumps(data))
        return resp.status_code == 200

    def get_domain(self):
        return self._get('%s/__erulb__/domain' % self.addr)

    def update_domain(self, backend_name, domain):
        data = {'backend': backend_name, 'name': domain}
        return self._put('%s/__erulb__/domain' % self.addr, data)

    def delete_domain(self, backend_name):
        data = {'backend': backend_name}
        return self._delete('%s/__erulb__/domain' % self.addr, data)

    def get_upstream(self):
        return self._get('%s/__erulb__/upstream' % self.addr)

    def update_upstream(self, backend_name, servers):
        data = {'backend': backend_name, 'servers': servers}
        return self._put('%s/__erulb__/upstream' % self.addr, data)

    def delete_upstream(self, backend_name):
        data = {'backend': backend_name}
        return self._delete('%s/__erulb__/upstream' % self.addr, data)


def add_record_rules(record):
    balancer = record.balancer
    client = LBClient(balancer.addr)

    # 1. 添加upstream
    # 现在还没加 weight
    servers = ['server %s;' % b for b in record.get_backends()]
    client.update_upstream(record.backend_name, servers)

    # 2. 添加domain
    client.update_domain(record.backend_name, record.domain)


def delete_record_rules(record):
    balancer = record.balancer
    client = LBClient(balancer.addr)

    # 1. 删除domain
    client.delete_domain(record.backend_name)

    # 2. 删除upstream
    client.delete_upstream(record.backend_name)
