# coding: utf-8

from datetime import datetime
from models.base import db, Base, PropsMixin, PropsItem
from models.consts import OPLOG_KIND_MAPPING, OPLOG_ACTION


DESC_MAPPING = {
    OPLOG_ACTION.create_project: '{self.user.uid}创建了项目{self.project_name}',
    OPLOG_ACTION.set_project_env: '{self.user.uid}为项目{self.project_name}设置了环境变量',
    OPLOG_ACTION.create_container: '{self.user.uid}创建了容器{self.container_id}',
    OPLOG_ACTION.delete_container: '{self.user.uid}删除了容器{self.container_id}',
    OPLOG_ACTION.stop_container: '{self.user.uid}停止了容器{self.container_id}',
    OPLOG_ACTION.start_container: '{self.user.uid}启动了容器{self.container_id}',
    OPLOG_ACTION.create_balancer: '{self.user.uid}创建了LB{self.balancer_id}',
    OPLOG_ACTION.delete_balancer: '{self.user.uid}删除了LB{self.balancer_id}',
    OPLOG_ACTION.create_lb_record: '{self.user.uid}创建了LB Record{self.record_id}',
    OPLOG_ACTION.delete_lb_record: '{self.user.uid}删除了LB Record{self.record_id}',
    OPLOG_ACTION.create_base_image: '{self.user.uid}创建了镜像{self.image}',
    OPLOG_ACTION.delete_base_image: '{self.user.uid}删除了镜像{self.image}',
    OPLOG_ACTION.grant_project: '{self.user.uid}给{self.acceptor}添加了项目{self.project_name}的权限',
    OPLOG_ACTION.grant_privilege: '{self.user.uid}把{self.acceptor}的权限修改为{self.privilege}',
    OPLOG_ACTION.build_image: '{self.user.uid}构建了镜像{self.image}',
}


class OPLog(Base, PropsMixin):

    __tablename__ = 'oplog'
    __table_args__ = (
        db.Index('user_kind', 'user_id', 'kind'),
    )

    user_id = db.Column(db.Integer, index=True)
    time = db.Column(db.DateTime, default=datetime.now)
    kind = db.Column(db.Integer, index=True)
    action = db.Column(db.Integer, index=True)

    project_name = PropsItem('project_name')
    container_id = PropsItem('container_id')
    balancer_id = PropsItem('balancer_id')
    image = PropsItem('image')
    privilege = PropsItem('privilege')
    acceptor = PropsItem('acceptor')
    record_id = PropsItem('record_id')
    data = PropsItem('data')

    def get_uuid(self):
        return '/ainur/oplog/%s' % self.id

    @classmethod
    def create(cls, user_id, action):
        kind = OPLOG_KIND_MAPPING.get(action, None)
        if kind is None:
            return None

        log = cls(user_id=user_id, kind=kind, action=action)
        db.session.add(log)
        db.session.commit()
        return log

    @classmethod
    def get_by_user_id(cls, user_id, kind=None, time=None, action=None, start=0, limit=20):
        q = cls.query.filter_by(user_id=user_id)
        if kind is not None:
            q = q.filter_by(kind=kind)
        if time is not None:
            q = q.filter_by(time=time)
        if action is not None:
            q = q.filter_by(action=action)
        q = q.order_by(cls.id.desc())
        return q[start:start+limit]

    @property
    def user(self):
        from .user import User
        return User.get(self.user_id)

    @property
    def description(self):
        formatter = DESC_MAPPING.get(self.action, '')
        return formatter.format(self=self)
