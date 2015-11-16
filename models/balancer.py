from werkzeug.utils import cached_property

from base import db, Base


class Balancer(Base):
    __tablename__ = 'balancer'

    container_id = db.Column(db.String(64), unique=True, nullable=False)


class BalancePlan(Base):
    __tablename__ = 'plan'

    project_name = db.Column(db.String(255), index=True, nullable=False)
    project_entrypoint = db.Column(db.String(255), nullable=False)
    balancer_id = db.Column(db.ForeignKey(Balancer.id), index=True)
    domain_name = db.Column(db.String(255), nullable=False)

    __table_args__ = (db.Index(
        'planset', 'project_name', 'project_entrypoint', 'balancer_id',
        'domain_name', unique=True),)
