from flask import render_template, Blueprint, request, g

from utils import demand_login, forbid
from models.balancer import BalancePlan

bp = Blueprint('lb', __name__, url_prefix='/lb')


@bp.route('/')
def index():
    return render_template('lb/index.html', page=g.page,
                           plans=BalancePlan.list(g.start, g.limit))


@bp.before_request
@demand_login
def access_control():
    if not g.user['lb']:
        return forbid()
