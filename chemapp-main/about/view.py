from flask import Blueprint, render_template

about_bp = Blueprint('about_bp', __name__, template_folder = "templates", static_folder = "static")
@about_bp.route('/about_bp')
def about():
    return render_template('about_bp.html')

#ref naar pagina
  