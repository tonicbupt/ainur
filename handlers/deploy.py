# coding: utf-8

import yaml

from eruhttp import EruException
from flask import render_template, Blueprint, request, g, abort

from config import APPNAME_ERU_LB
from libs.utils import json_api, parse_git_url
from libs.clients import gitlab, eru

from models.image import BaseImage
from models.oplog import OPLog
from models.project import Project
from models.consts import OPLOG_ACTION, OPLOG_KIND


bp = Blueprint('deploy', __name__, url_prefix='/deploy')


@bp.route('/')
def deploy():
    projects = g.user.get_accessible_projects(start=g.start, limit=g.limit)
    return render_template('/deploy/index.html', projects=projects)


@bp.route('/oplog/')
def oplog():
    logs = OPLog.get_by_user_id(g.user.id, kind=OPLOG_KIND.project, start=g.start, limit=g.limit)
    return render_template('/deploy/logs.html', logs=logs)


def _get_project(repo_url):
    repo = parse_git_url(repo_url)
    project = gitlab.getproject(repo)
    if not project:
        return None
    return project


def _get_project_commits(repo_url):
    project = _get_project(repo_url)
    if not project:
        return []
    return gitlab.getrepositorycommits(project['id'], page=0)


def _get_rev_appyaml(project_id, commit_id):
    appyaml = gitlab.getrawfile(project_id, commit_id, 'app.yaml')
    if not appyaml:
        return {}
    return yaml.load(appyaml)


def _register_app(repo_url, commit_id=None):
    project = _get_project(repo_url)
    if commit_id is None:
        commits = gitlab.getrepositorycommits(project['id'], ref_name='master',
                                              page=0, per_page=1)
        if len(commits) == 0:
            raise ValueError('Project %s has no commits' % repo_url)

        commit_id = commits[0]['id']

    appconfig = _get_rev_appyaml(project['id'], commit_id)
    if not appconfig:
        raise ValueError('app.yaml of %s is empty' % repo_url)

    eru.register_app_version(commit_id, repo_url, '', appconfig)
    return appconfig


@bp.route('/project/new')
def new():
    return render_template('/deploy/projects/new.html')


@bp.route('/project/<name>/detail/')
def detail(name):
    project = Project.get_by_name(name)
    if not project:
        abort(404)
    return render_template('/deploy/projects/detail.html', project=project)


@bp.route('/project/<name>/tasks/')
def tasks(name):
    tasks = eru.list_app_tasks(name, g.start, g.limit)
    tasks = tasks['tasks']
    return render_template('/deploy/projects/images_tasks.html', tasks=tasks, name=name)


@bp.route('/project/<name>/build_image/')
def build_image(name):
    project = Project.get_by_name(name)
    if not project:
        abort(404)

    revisions = _get_project_commits(project.git)
    pods = eru.list_group_pods(g.user.group)
    base_images = BaseImage.list_all()
    return render_template(
        '/deploy/projects/build_image.html', project=project,
        revisions=revisions, pods=pods, base_images=base_images)


@bp.route('/project/<name>/envs/')
def environments(name):
    envs = eru.list_app_env_names(name)
    envs = envs['data']
    return render_template('/deploy/projects/envs.html', envs=envs, name=name)


@bp.route('/project/<name>/envs/<env_name>/')
def env_detail(name, env_name):
    env_content = eru.list_app_env_content(name, env_name)
    env_content = env_content['data']
    return render_template('/deploy/projects/env_detail.html',
            env_content=env_content, name=name, env_name=env_name)


@bp.route('/project/<name>/containers/')
def containers(name):
    containers = eru.list_app_containers(name)
    containers = containers['containers']
    return render_template('/deploy/projects/containers.html',
            containers=containers, name=name)


@bp.route('/projects/<name>/deploy/')
def deploy_container(name):
    images = eru.list_app_images(name)
    image_names = [i['image_url'] for i in images]

    envs = eru.list_app_env_names(name)['data']
    pods = eru.list_group_pods(g.user.group)
    networks = eru.list_network()

    return render_template('/deploy/projects/deploy_container.html',
            images=image_names, envs=envs, pods=pods, name=name,
            networks=networks)


@bp.route('/pods/')
def pods_list():
    pods = eru.list_pods(g.start, g.limit)
    return render_template('/deploy/pods/index.html', pods=pods)


@bp.route('/pods/<pod_name>/hosts/')
def pod_hosts(pod_name):
    hosts = eru.list_pod_hosts(pod_name, g.start, g.limit)
    return render_template('/deploy/pods/hosts.html', page=g.page,
            pod_name=pod_name, hosts=hosts)


@bp.route('/hosts/<host_name>/containers/')
def host_containers(host_name):
    host = eru.get_host(host_name)
    if host is None:
        abort(404)

    pod_name=eru.get_pod(host['pod_id'])['name']
    containers=eru.list_host_containers(host_name, g.start, g.limit)['containers']
    return render_template('/deploy/pods/host_containers.html', host_name=host_name,
            pod_name=pod_name, containers=containers)


@bp.route('/api/groups')
@json_api
def deploy_groups():
    return [[g['id'], g['name']] for g in eru.list_groups()]


@bp.route('/api/projects/register', methods=['POST'])
@json_api
def api_register():
    repo_url = request.form['repo_url']
    app = _register_app(repo_url)
    project_name = app['appname']

    log = OPLog.create(g.user.id, OPLOG_ACTION.create_project)
    log.project_name = project_name
    return project_name


@bp.route('/api/pods')
@json_api
def list_pods():
    return [p['name'] for p in eru.list_pods()]


@bp.route('/api/pods/<pod_name>/list_hosts')
@json_api
def list_hosts_in_pod(pod_name):
    return eru.list_pod_hosts(pod_name, g.start, g.limit)


@bp.route('/api/project/build_image', methods=['POST'])
@json_api
def api_build_image():
    name = request.form['project']
    app = eru.get_app(name)

    revision = request.form['revision']
    _register_app(app['git'], revision)
    _get_project(app['git'])

    pod = request.form['pod']
    image = 'docker-registry.intra.hunantv.com/nbeimage/%s' % request.form['image']
    eru.build_image(g.user.group, pod, app['name'], image, revision)

    log = OPLog.create(g.user.id, OPLOG_ACTION.build_image)
    log.image = image


@bp.route('/api/revision/list_entrypoints', methods=['GET'])
@json_api
def revision_list_entrypoints():
    print request.args
    project = _get_project(eru.get_app(request.args['project'])['git'])
    y = _get_rev_appyaml(project['id'], request.args['commit'])
    return y['entrypoints'].keys()


def _lastest_version_sha(what):
    try:
        return eru.list_app_versions(what)['versions'][0]['sha']
    except LookupError:
        raise EruException('eru fail to give version SHA of ' + what)


@bp.route('/api/revision/list_entrypoints_for_latest_ver', methods=['GET'])
@json_api
def revision_list_entrypoints_for_latest_ver():
    p = request.args['project']
    project = _get_project(eru.get_app(p)['git'])
    y = _get_rev_appyaml(project['id'], _lastest_version_sha(p))
    return y['entrypoints'].keys()


@bp.route('/api/project/deploy_container', methods=['POST'])
@json_api
def deploy_container_api():
    form = request.form
    project = form['project']
    if project == APPNAME_ERU_LB:
        raise ValueError('Unable to deploy eru-lb, do it on load balance page')

    eru.deploy_private(
        group_name=g.user.group,
        pod_name=form['pod'],
        app_name=project,
        ncore=form.get('ncore', type=float),
        ncontainer=form.get('ncontainer', type=int),
        version=form['version'],
        entrypoint=form['entrypoint'],
        env=form['env'],
        network_ids=form.getlist('network'),
        host_name=form.get('host'),
        args=form['extendargs'].split(' '),
    )

    OPLog.create(g.user.id, OPLOG_ACTION.create_container)


@bp.route('/api/containers', methods=['GET'])
@json_api
def get_containers():
    appname = request.args.get('app', '')
    if not appname:
        raise ValueError('Need appname set')

    version = request.args.get('version', '')
    if version:
        return eru.list_version_containers(appname, version, g.start, g.limit)
    return eru.list_app_containers(appname, g.start, g.limit)


@bp.route('/api/project/save_env', methods=['POST'])
@json_api
def set_project_env():
    form = request.form
    project = form['project']
    env = form['env']
    content = {}

    for line, i in enumerate(form['content'].split('\n')):
        if not i.strip():
            continue

        kv = i.split('=', 1)
        if len(kv) == 1:
            raise ValueError('invalid env item %s at line %d' % (i, line + 1))

        content[kv[0].strip()] = kv[1].strip()

    try:
        eru.set_app_env(project, env, **content)
    except Exception as e:
        print e.message
    log = OPLog.create(g.user.id, OPLOG_ACTION.set_project_env)
    log.data = content
    log.project_name = project


@bp.route('/api/tasklog/<int:task_id>')
@json_api
def get_task_log(task_id):
    return eru.get_task_log(task_id)


@bp.route('/api/containers/stop', methods=['POST'])
@json_api
def stop_container():
    cid = request.form['id']
    if eru.get_container(cid)['appname'] == APPNAME_ERU_LB:
        raise ValueError('Unable to stop eru-lb, do it on load balance page')

    eru.stop_container(cid)
    log = OPLog.create(g.user.id, OPLOG_ACTION.stop_container)
    log.container_id = cid


@bp.route('/api/containers/start', methods=['POST'])
@json_api
def start_container():
    cid = request.form['id']
    eru.start_container(cid)

    log = OPLog.create(g.user.id, OPLOG_ACTION.start_container)
    log.container_id = cid


@bp.route('/api/containers/remove', methods=['POST'])
@json_api
def rm_container():
    cid = request.form['id']
    if eru.get_container(cid)['appname'] == APPNAME_ERU_LB:
        raise ValueError('Unable to remove eru-lb, do it on load balance page')

    eru.remove_containers([cid])

    log = OPLog.create(g.user.id, OPLOG_ACTION.delete_container)
    log.container_id = cid
