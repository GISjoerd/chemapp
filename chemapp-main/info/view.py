from flask import Blueprint, render_template

info_bp = Blueprint('info_bp', __name__, template_folder = "templates", static_folder = "static")
@info_bp.route('/info_bp')
def info():
    return render_template('info_bp.html')
