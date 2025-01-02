from pkgutil import get_data
from flask import render_template, request, url_for, redirect, flash, session, g, request,session,Blueprint


from .. import login_required



facturas_bp = Blueprint('facturas', __name__, template_folder='../../templates/facturas', static_folder='../../static')

# ruta principal de inicio

@facturas_bp.route('/facturas',methods = ('GET', 'POST'))
def facturas_tcp():

    return render_template ("panel/panel_tcp.html")
