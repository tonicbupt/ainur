import yaml
import json
import logging
from datetime import date, datetime
from flask import render_template, Blueprint, request, g
from redis.exceptions import RedisError
from eruhttp import EruException

from utils import json_api, post_form, parse_git_url, not_found, demand_login
from clients import gitlab, eru
from .ext import rds, safe_rds_get, safe_rds_set

bp = Blueprint('deploy', __name__, url_prefix='/deploy')


@bp.route('/audit/logs')
@demand_login
def audit_logs():
    dt = request.query_string or date.today().strftime('%Y-%m-%d')
    return render_template('deploy/audit/logs.html', date=dt, logs=[
        json.loads(x) for x in rds.lrange('task:%s' % dt, 0, -1)])


def _get_project(repo_url):
    logging.debug('Get repo %s', repo_url)
    repo = parse_git_url(repo_url)
    logging.debug('Get project %s', repo)

    rds_key = 'project:%s' % repo
    project = safe_rds_get(rds_key)
    if project is not None:
        logging.debug('Hit project cache %s', repo)
        return project

    project = gitlab.getproject(repo)
    if not project:
        raise ValueError('no such repository %s' % repo_url)

    safe_rds_set(rds_key, project)
    return project


def _get_project_commits(repo_url):
    project = _get_project(repo_url)
    return gitlab.getrepositorycommits(project['id'], page=0)


def _get_rev_appyaml(project_id, commit_id):
    rds_key = 'appyaml:%s:%s' % (project_id, commit_id[:7])
    appyaml = safe_rds_get(rds_key)
    if appyaml is not None:
        logging.debug('Hit appyaml cache %s/%s', project_id, commit_id)
        return appyaml
    appyaml = gitlab.getrawfile(project_id, commit_id, 'app.yaml')
    if not appyaml:
        raise ValueError('no app.yaml in %s' % project_id)
    appyaml = yaml.load(appyaml)
    safe_rds_set(rds_key, appyaml)
    return appyaml


def _register_app(repo_url, commit_id=None):
    project = _get_project(repo_url)
    logging.debug('Get app.yaml for %s:%s', project['id'],
                  project['name_with_namespace'])
    if commit_id is None:
        commits = gitlab.getrepositorycommits(project['id'], ref_name='master',
                                              page=0, per_page=1)
        if len(commits) == 0:
            raise ValueError('Project %s has no commits' % repo_url)
        commit_id = commits[0]['id']
    appconfig = _get_rev_appyaml(project['id'], commit_id)
    logging.debug('Loaded app.yaml for %s', appconfig['appname'])
    logging.info('Register app=%s commit=%s repo=%s', appconfig['appname'],
                 commit_id, repo_url)
    eru.register_app_version(commit_id, repo_url, '', appconfig)
    return appconfig


@bp.route('/')
def deploy():
    return render_template('deploy/index.html', page=g.page,
                           projects=eru.list_apps(g.start, g.limit))


@bp.route('/projects/new')
@demand_login
def projects_new():
    return render_template('deploy/projects/new.html')


@bp.route('/projects/detail/<project_name>')
def project_detail(project_name):
    try:
        project = eru.get_app(project_name)
    except EruException as e:
        return render_template(
            'deploy/projects/detail_notfound.html', project=project_name), 404
    return render_template('deploy/projects/detail.html', project=project)


@bp.route('/projects/images/<project_name>')
def project_images_tasks(project_name):
    return render_template(
        'deploy/projects/images_tasks.html', page=g.page,
        tasks=eru.list_app_tasks(project_name, g.start, g.limit)['tasks'],
        project_name=project_name)


@bp.route('/projects/build_image/<project_name>')
@demand_login
def project_build_image_entry(project_name):
    app = eru.get_app(project_name)
    try:
        return render_template(
            'deploy/projects/build_image.html', project=app,
            revisions=_get_project_commits(app['git']), pods=eru.list_pods(),
            base_images=rds.lrange('base_images', 0, -1))
    except RedisError as e:
        return 'Unable to list base images, Redis is down: %s' % e, 500


@bp.route('/projects/envs/<project_name>')
def project_environments(project_name):
    return render_template(
        'deploy/projects/envs.html',
        envs=eru.list_app_env_names(project_name)['data'],
        project_name=project_name)


@bp.route('/projects/envs/<project_name>/<env_name>')
@demand_login
def project_env_detail(project_name, env_name):
    return render_template(
        'deploy/projects/env_detail.html',
        env_content=eru.list_app_env_content(project_name, env_name)['data'],
        project_name=project_name, env_name=env_name)


@bp.route('/projects/containers/<project_name>')
@demand_login
def project_containers(project_name):
    return render_template(
        'deploy/projects/containers.html',
        containers=eru.list_app_containers(project_name)['containers'],
        project_name=project_name)


def _get_user_group():
    if not g.user:
        return None
    return 'platform'


@bp.route('/projects/deploy_container/<project_name>')
@demand_login
def project_deploy_container(project_name):
    images = eru.list_app_images(project_name)
    image_names = [i['image_url'] for i in images]
    return render_template(
        'deploy/projects/deploy_container.html', images=image_names,
        envs=eru.list_app_env_names(project_name)['data'],
        pods=eru.list_group_pods(_get_user_group()), project_name=project_name,
        networks=eru.list_network())


@bp.route('/pods/')
def pods_list():
    return render_template('deploy/pods/index.html', page=g.page,
                           pods=eru.list_pods(g.start, g.limit))


@bp.route('/pods/<pod_name>/hosts/')
def pod_hosts(pod_name):
    return render_template(
        'deploy/pods/hosts.html', page=g.page, pod_name=pod_name,
        hosts=eru.list_pod_hosts(pod_name, g.start, g.limit))


@bp.route('/hosts/<host_name>/containers/')
@demand_login
def host_containers(host_name):
    host = eru.get_host(host_name)
    if host is None:
        return not_found()
    return render_template(
        'deploy/pods/host_containers.html', page=g.page, host_name=host_name,
        pod_name=eru.get_pod(host['pod_id'])['name'],
        containers=eru.list_host_containers(
            host_name, g.start, g.limit)['containers'])


@bp.route('/api/groups')
@demand_login
@json_api
def deploy_groups():
    return [[g['id'], g['name']] for g in eru.list_groups()]


@bp.route('/api/projects/register', methods=['POST'])
@demand_login
@json_api
def register_project():
    args = post_form()
    app = _register_app(args['repo_url'])
    return app['appname']


@bp.route('/api/pods')
@demand_login
@json_api
def list_pods():
    return [p['name'] for p in eru.list_pods()]


@bp.route('/api/pods/<pod_name>/list_hosts')
@demand_login
@json_api
def list_hosts_in_pod(pod_name):
    return eru.list_pod_hosts(pod_name, g.start, g.limit)


def _push_to_today_task(act, args):
    task_key = date.today().strftime('task:%Y-%m-%d')
    rds.lpush(task_key, json.dumps({
        'time': datetime.now().strftime('%H:%M:%S'),
        'user': g.user['uid'],
        'act': act,
        'args': args,
    }))
    rds.expire(task_key, SIX_MONTHS)

SIX_MONTHS = 86400 * 30 * 6


@bp.route('/api/projects/build_image', methods=['POST'])
@demand_login
@json_api
def project_build_image():
    args = post_form()
    logging.info('To build image project=%s revision=%s pod=%s image=%s',
                 args['project'], args['revision'], args['pod'], args['image'])
    app = eru.get_app(args['project'])
    revision = args['revision']
    _register_app(app['git'], revision)
    project = _get_project(app['git'])
    pod = args['pod']
    group = _get_user_group()
    image = 'docker-registry.intra.hunantv.com/nbeimage/%s' % args['image']
    logging.info('Start building group=%s pod=%s app=%s image=%s rev=%s',
                 group, pod, app['name'], image, revision)
    eru.build_image(group, pod, app['name'], image, revision)
    _push_to_today_task('build_image', args)


@bp.route('/api/revision/list_entrypoints', methods=['GET'])
@demand_login
@json_api
def revision_list_entrypoints():
    project = _get_project(eru.get_app(request.args['project'])['git'])
    y = _get_rev_appyaml(project['id'], request.args['commit'])
    return y['entrypoints'].keys()


@bp.route('/api/projects/deploy_container', methods=['POST'])
@demand_login
@json_api
def project_deploy_container_api():
    args = request.form
    eru.deploy_private(
        group_name=_get_user_group(),
        pod_name=args['pod'],
        app_name=args['project'],
        ncore=float(args['ncore']),
        ncontainer=int(args['ncontainer']),
        version=args['version'],
        entrypoint=args['entrypoint'],
        env=args['env'],
        network_ids=args.getlist('network'),
        host_name=args.get('host'),
    )
    _push_to_today_task('deploy', args)


@bp.route('/api/containers', methods=['GET'])
@demand_login
@json_api
def get_containers():
    appname = request.args.get('app', '')
    if not appname:
        raise ValueError('Need appname set')

    version = request.args.get('version', '')
    if version:
        return eru.list_version_containers(appname, version, g.start, g.limit)
    return eru.list_app_containers(appname, g.start, g.limit)


@bp.route('/api/projects/save_env', methods=['POST'])
@demand_login
@json_api
def set_project_env():
    args = post_form()
    project = args['project']
    env = args['env']
    content = {}
    for line, i in enumerate(args['content'].split('\n')):
        if len(i.strip()) == 0:
            continue
        kv = i.split('=', 1)
        if len(kv) == 1:
            raise ValueError('invalid env item %s at line %d' % (i, line + 1))
        content[kv[0].strip()] = kv[1].strip()
    eru.set_app_env(project, env, **content)
    _push_to_today_task('edit_env', args)


@bp.route('/api/tasklog/<int:task_id>')
@demand_login
@json_api
def get_task_log(task_id):
    return eru.get_task_log(task_id)


@bp.route('/api/containers/stop', methods=['POST'])
@demand_login
@json_api
def stop_container():
    cid = post_form()['id']
    logging.info('Stop container %s', cid)
    eru.stop_container(cid)
    _push_to_today_task('stop', cid)


@bp.route('/api/containers/start', methods=['POST'])
@demand_login
@json_api
def start_container():
    cid = post_form()['id']
    logging.info('Start container %s', cid)
    eru.start_container(cid)
    _push_to_today_task('start', cid)


@bp.route('/api/containers/remove', methods=['POST'])
@demand_login
@json_api
def rm_container():
    cid = post_form()['id']
    logging.info('Remove container %s', cid)
    eru.remove_containers([cid])
    _push_to_today_task('remove', cid)
