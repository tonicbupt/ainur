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
        r = cls()
        r.appname = appname
        r.entrypoint = entrypoint
        r.domain = r.domain
        r.balancer_id = balancer_id
        db.session.add(r)
        db.session.commit()
        return r

    @classmethod
    def get_by_balancer_id(cls, balancer_id):
        return cls.query.filter_by(balancer_id=balancer_id).order_by(cls.id.desc()).all()

    @property
    def backend_name(self):
        return '%s:%s' % (self.appname, self.entrypoint)

    def get_backends(self):
        backends = []
        containers = eru.list_app_containers(self.appname, limit=100)
        for container in containers['containers']:
            if container['entrypoint'] != self.entrypoint:
                continue
            backends.extend(container['backends'])
        return backends


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
    def get(cls, id):
        return cls.query.filter_by(id=id).first()

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
        return BalanceRecord.create(appname, entrypoint, domain)

    def get_records(self):
        return BalanceRecord.get_by_balancer_id(self.id)


def update_record(balancer, record):
    if not record:
        return

    headers = {'Host': balancer.api_url}

    # 1. 添加upstream
    upstream_url = balancer.addr + '/upstream'
    # 现在还没加 weight
    backends = record.get_backends()
    payload = {
        'backend': record.backend_name,
        'servers': ['server %s;' for b in backends],
    }
    r = requests.put(upstream_url, headers=headers, data=json.dumps(payload))
    if r.json()['msg'] != 'ok':
        return False

    # 2. 添加domain
    domain_url = balancer.addr + '/domain'
    payload = {
        'backend': record.backend_name,
        'name': record.domain,
    }
    r = requests.put(domain_url, headers=headers, data=json.dumps(payload))
    return r.json()['msg'] == 'ok'
