from flask import render_template
from app.main import main_bp


# ruta principal de inicio
@main_bp.route('/')
def index():
    return render_template('index.html')

# proyecto flujorad web

@main_bp.route('/flujorad')
def flujorad():
    return render_template('flujorad.html')




