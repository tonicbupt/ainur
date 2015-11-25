# coding: utf-8

from collections import namedtuple

# NOTE: 如果有新增必须是增加
# 否则会扰乱类型的顺序的
OPLOG_ACTION_NAMES = [
    'create_project',
    'set_project_env',
    'create_container',
    'delete_container',
    'stop_container',
    'start_container',
    'create_balancer',
    'delete_balancer',
    'create_lb_record',
    'delete_lb_record',
    'create_base_image',
    'delete_base_image',
    'grant_project',
    'grant_privilege',
    'build_image',
]
OPLOG_KIND_NAMES = [
    'project',
    'balancer',
    'admin',
]

OPLOG_ACTION = namedtuple('OPLogAction', OPLOG_ACTION_NAMES)(*range(len(OPLOG_ACTION_NAMES)))
OPLOG_KIND = namedtuple('OPLogKind', OPLOG_KIND_NAMES)(*range(len(OPLOG_KIND_NAMES)))
OPLOG_KIND_MAPPING = {
    OPLOG_ACTION.create_project: OPLOG_KIND.project,
    OPLOG_ACTION.set_project_env: OPLOG_KIND.project,
    OPLOG_ACTION.create_container: OPLOG_KIND.project,
    OPLOG_ACTION.delete_container: OPLOG_KIND.project,
    OPLOG_ACTION.stop_container: OPLOG_KIND.project,
    OPLOG_ACTION.start_container: OPLOG_KIND.project,
    OPLOG_ACTION.build_image: OPLOG_KIND.project,

    OPLOG_ACTION.create_balancer: OPLOG_KIND.balancer,
    OPLOG_ACTION.delete_balancer: OPLOG_KIND.balancer,
    OPLOG_ACTION.create_lb_record: OPLOG_KIND.balancer,
    OPLOG_ACTION.delete_lb_record: OPLOG_KIND.balancer,
    OPLOG_ACTION.create_balancer: OPLOG_KIND.balancer,

    OPLOG_ACTION.create_base_image: OPLOG_KIND.admin,
    OPLOG_ACTION.delete_base_image: OPLOG_KIND.admin,
    OPLOG_ACTION.grant_project: OPLOG_KIND.admin,
    OPLOG_ACTION.grant_privilege: OPLOG_KIND.admin,
}

LB_IMAGE = 'docker-registry.intra.hunantv.com/erulb:345be25'
LB_ENTRY_BETA = 'beta-host'
LB_ENV_BETA = 'beta'
LB_ENTRY_RELEASE = 'release-host'
LB_ENV_RELEASE = 'release'

USER_ROLE = namedtuple('UserRole', ['user', 'admin', 'lb'])(1, 2, 4)
