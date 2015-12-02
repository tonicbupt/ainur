# coding: utf-8

import json
import requests
import sqlalchemy.exc

from libs.clients import eru
from models.base import db, Base, PropsMixin, PropsItem


class BalanceRecord(Base, PropsMixin):

    __tablename__ = 'balancer_record'
    __table_args = (
        db.UniqueConstraint('balancer_id', 'appname', 'entrypoint'),
    )

    appname = db.Column(db.String(255), index=True)
    entrypoint = db.Column(db.String(255), index=True)
    domain = db.Column(db.String(255))
    balancer_id = db.Column(db.Integer)

    analysis_switch = PropsItem('analysis_switch', type=bool, default=False)

    def get_uuid(self):
        return '/ainur/balance_record/%s' % self.id

    @classmethod
    def create(cls, appname, entrypoint, domain, balancer_id):
        try:
            r = cls(appname=appname, entrypoint=entrypoint, domain=domain, balancer_id=balancer_id)
            db.session.add(r)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
            return None

        add_record_rules(r)
        return r

    @classmethod
    def get_by_balancer_id(cls, balancer_id):
        return cls.query.filter_by(balancer_id=balancer_id).order_by(cls.id.desc()).all()

    @classmethod
    def get_by_appname_and_entrypoint(cls, appname, entrypoint):
        return cls.query.filter_by(appname=appname, entrypoint=entrypoint).order_by(cls.id.desc()).all()

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

    def __hash__(self):
        return self.id

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

    @property
    def lb_client(self):
        return LBClient(self.addr)

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

    def to_dict(self):
        d = {}
        d['user_id'] = self.user_id
        d['group'] = self.group
        d['lb_client'] = self.lb_client.to_dict()
        return d


class LBClient(object):

    def __init__(self, addr):
        if not addr.startswith('http://'):
            addr = 'http://%s' % addr
        self.addr = addr
        self.domain_addr = '%s/__erulb__/domain' % addr
        self.upstream_addr = '%s/__erulb__/upstream' % addr
        self.analysis_addr = '%s/__erulb__/analysis' % addr

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
        return self._get(self.domain_addr)

    def update_domain(self, backend_name, domain):
        data = {'backend': backend_name, 'name': domain}
        return self._put(self.domain_addr, data)

    def delete_domain(self, domain):
        data = {'name': domain}
        return self._delete(self.domain_addr, data)

    def get_upstream(self):
        return self._get(self.upstream_addr)

    def update_upstream(self, backend_name, servers):
        data = {'backend': backend_name, 'servers': servers}
        return self._put(self.upstream_addr, data)

    def delete_upstream(self, backend_name):
        data = {'backend': backend_name}
        return self._delete(self.upstream_addr, data)

    def add_analysis(self, domain):
        if not isinstance(domain, list):
            domain = [domain]
        data = {'hosts': domain}
        return self._put(self.analysis_addr, data)

    def delete_analysis(self, domain):
        data = {'host': domain}
        return self._delete(self.analysis_addr, data)

    def get_analysis(self):
        return self._get(self.analysis_addr)

    def to_dict(self):
        return {'domain_addr': self.domain_addr, 'upstream_addr': self.upstream_addr}


def add_record_rules(record):
    client = record.balancer.lb_client

    # 1. 添加upstream
    # 现在还没加 weight
    servers = ['server %s;' % b for b in record.get_backends()]
    client.update_upstream(record.backend_name, servers)

    # 2. 添加domain
    client.update_domain(record.backend_name, record.domain)


def delete_record_rules(record):
    client = record.balancer.lb_client

    # 1. 删除domain
    client.delete_domain(record.backend_name)

    # 2. 删除upstream
    client.delete_upstream(record.backend_name)


def add_record_analysis(record):
    client = record.balancer.lb_client
    client.add_analysis(record.domain)


def delete_record_analysis(record):
    client = record.balancer.lb_client
    client.delete_analysis(record.domain)
