# coding: utf-8

from models.balancer import BalanceRecord
from . import create_api_blueprint


bp = create_api_blueprint('ajax_lb', __name__, url_prefix='/ajax/lb')


@bp.route('/<appname>/<entrypoint>/', methods=['GET'])
def get_balancer_for_app(appname, entrypoint):
    records = BalanceRecord.get_by_appname_and_entrypoint(appname, entrypoint)
    if not records:
        return None
    data = {'backend_name': records[0].backend_name}
    data['balancers'] = list(set([r.balancer for r in records]))
    return data
