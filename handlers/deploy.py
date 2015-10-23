import logging
import yaml
from flask import render_template, Blueprint, request

from utils import send_template, json_api, post_json
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
    if not repo_url.startswith('git@git.hunantv.com:'):
        raise ValueError('no such repository')
    repo = repo_url.split(':')[-1]
    if repo.endswith('.git'):
        repo = repo[:-4]
    repo = repo.replace('/', '%2f')
    logging.debug('Get project %s', repo)
    project = gitlab.getproject(repo)
    if project == False:
        raise ValueError('no such repository')
    logging.debug('Get app.yaml for %s:%s', project['id'],
                  project['name_with_namespace'])
    appyaml = gitlab.getrawfile(project['id'], 'master', 'app.yaml')
    if appyaml == False:
        raise ValueError('no app.yaml in repository')
    commit_id = gitlab.getrepositorycommit(project['id'], 'master')['id']
    appconfig = yaml.load(appyaml)
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
        "build_script": [
            "pip install -r requirements.txt",
            "echo OK",
        ],
    }


@bp.route('/api/projects/<int:project_id>/git_refs')
@json_api
def project_git_refs(project_id):
    return [{
        'ref_type': 'branch',
        'name': '%s - %s' % (c['id'][:7], c['title']),
        'hexsha': c['id'],
        'message': c['message'],
    } for c in gitlab.getrepositorycommits(project_id)]


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

    project_id = request.args.get('project_id')
    page = int(request.args.get('page', 1))
    if project_id is not None:
        appname = gitlab.getproject(int(project_id))['name']
        return format_versions(eru.list_app_versions(
            appname, (page - 1) * 40, 40)['versions'])
    return format_versions([{
        'app_id': 4202,
        'appconfig': {
            'appname': 'redis-ctl',
            'build': 'pip install -r requirements.txt',
            'entrypoints': {
                'daemon': {'cmd': 'python daemon.py'},
                'releaselock': {u'cmd': u'python release_task_lock.py'},
                'web': {u'cmd': u'python main.py', u'ports': [u'5000/tcp']}
            }
        },
        'created': '2015-07-30 18:44:27',
        'id': 10334,
        'name': 'redis-ctl',
        'sha': '9cebe86466c1700b4a8121bbe20808ef9c6abeb0',
    }])


@bp.route('/api/project_versions', methods=['POST'])
@json_api
def project_build_image():
    args = post_json()
    project = gitlab.getproject(int(args['project_id']))
    group, app = project['name_with_namespace'].split('/')
    pod = args['pod']
    base_image = ('docker-registry.intra.hunantv.com/nbeimage/' +
                  args['base_image'])
    version = args['ref_hexsha1']
    logging.info('Start building group=%s pod=%s app=%s image=%s version=%s',
                 group, pod, app, base_image, version)
    eru.build_image(group, pod, app, base_image, version)
    return ''


@bp.route('/<path:templ>')
def deploy_templ(templ):
    return send_template('deploy', templ)
