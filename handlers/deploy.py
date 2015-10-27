# coding: utf-8

import yaml
import logging
from flask import render_template, Blueprint, request, g

from utils import send_template, json_api, post_json, parse_git_url
from clients import gitlab, eru


bp = Blueprint('deploy', __name__, url_prefix='/deploy')


@bp.route('/')
def deploy():
    return render_template('deploy/app.html')


@bp.route('/api/groups')
@json_api
def deploy_groups():
    return [[g['id'], g['name']] for g in eru.list_groups()]


@bp.route('/api/projects', methods=['GET'])
@json_api
def deploy_projects():
    ''' Args:
        * [group_id]
        * [name_icontain]
        * [page]
    '''
    return [{
        'id': 0,
        'name': 'ainur',
        'repo_url': 'git@git.hunantv.com:platform/ainur.git',
        'enable_ci': False,
        'online_ver': '525bff4',
        'group_id': 0,
        'group': {'id': 0, 'name': 'Platform'},
    }]


@bp.route('/api/projects', methods=['POST'])
@json_api
def register_project():
    args = post_json()

    repo_url = args['repo_url']
    repo = parse_git_url(repo_url)
    logging.debug('Get project %s', repo)

    project = gitlab.getproject(repo)
    if not project:
        raise ValueError('No such repository')

    logging.debug('Get app.yaml for %s:%s', project['id'], project['name_with_namespace'])

    appyaml = gitlab.getrawfile(project['id'], 'master', 'app.yaml')
    if not appyaml:
        raise ValueError('no app.yaml in repository')
    appconfig = yaml.load(appyaml)

    commit_id = gitlab.getrepositorycommit(project['id'], 'master')['id']
    logging.debug('Loaded app.yaml for %s / %s', appconfig['appname'], appyaml)

    eru.register_app_version(commit_id, repo_url, None, appconfig)
    return ''


@bp.route('/api/pods')
@json_api
def list_pods():
    return [p['name'] for p in eru.list_pods()]


@bp.route('/api/base_images')
@json_api
def base_iamges():
    return ['ubuntu:binary-2015.09.06', 'ubuntu:python-2015.09.06',
            'ubuntu:pywebstd-2015.09.18']


@bp.route('/api/projects/<int:project_id>')
@json_api
def project_detail(project_id):
    p = gitlab.getproject(project_id)
    if not p:
        raise ValueError('No project named %s' % project_id)

    appyaml = gitlab.getrawfile(p['id'], 'master', 'app.yaml')
    if not appyaml:
        raise ValueError('No app.yaml set for project %s' % project_id)

    appconfig = yaml.load(appyaml)
    build = appconfig.get('build', [])
    if not isinstance(build, list):
        build = [build, ]

    return {
        "id": project_id,
        "name": p['name'],
        "repo_url": p['ssh_url_to_repo'],
        "base_image": "----",
        "online_ver": "----",
        "enable_ci": False,
        "comment": '----',
        "group_id": p['namespace']['id'],
        "group": {
            "id": p['namespace']['id'],
            "name": p['namespace']['name'],
        },
        "build_script": build,
    }


@bp.route('/api/projects/<int:project_id>/git_refs')
@json_api
def project_git_refs(project_id):
    commits = gitlab.getrepositorycommits(project_id) or []
    return [{
        'ref_type': 'branch',
        'name': '%s - %s' % (c['id'][:7], c['title']),
        'hexsha': c['id'],
        'message': c['message'],
    } for c in commits]


@bp.route('/api/project_versions', methods=['GET'])
@json_api
def project_versions():
    def format_versions(versions):
        return [{
            "id": v['id'],
            "ref_name": "master",
            "ref_hexsha1": v['sha'],
            "version": v['sha'],
            "status": 1,
            "status_name": "----",
            "project_id": 0,
            "created_at": v['created'],
        } for v in versions]

    project_id = request.args.get('project_id', '')
    page = request.args.get('page', default=1, type=int)

    if not project_id:
        raise ValueError('Need project_id')

    project = gitlab.getproject(project_id)
    if not project:
        raise ValueError('Project not found %s' % project_id)

    appname = project['name']
    return format_versions(eru.list_app_versions(appname, (page - 1) * 40, 40)['versions'])


@bp.route('/api/project_versions', methods=['POST'])
@json_api
def project_build_image():
    args = post_json()

    project = gitlab.getproject(args['project_id'])
    if project:
        raise ValueError('Project not found %s' % project)

    # TODO 这个 group 似乎不是这个吧...
    group, app = project['name_with_namespace'].split('/')
    pod = args['pod']
    version = args['ref_hexsha1']
    base_image = 'docker-registry.intra.hunantv.com/nbeimage/%s' % args['base_image']

    logging.info('Start building group=%s pod=%s app=%s image=%s version=%s',
                 group, pod, app, base_image, version)
    return eru.build_image(group, pod, app, base_image, version)


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


@bp.route('/<path:templ>')
def deploy_templ(templ):
    return send_template('deploy', templ)
