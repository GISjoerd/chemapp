from flask import Blueprint, render_template

home_bp = Blueprint('home_bp', __name__, template_folder = "templates", static_folder = "static")
    # route to homepage
@home_bp.route("/")
def home():
    return render_template("home_bp.html")

#ref naar pagina
  