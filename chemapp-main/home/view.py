from flask import Blueprint, render_template

home_bp = Blueprint('home_bp', __name__, template_folder = "templates", static_folder = "static")
    # route to homepage
@home_bp.route("/")
def home():
    return render_template("home_bp.html")


about_bp = Blueprint('about_bp', __name__, template_folder = "templates", static_folder = "static")
@about_bp.route('/about_bp')
def about():
    return render_template('about_bp.html') 

#ref naar pagina
  