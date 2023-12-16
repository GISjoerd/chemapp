from flask import Blueprint, render_template

music_bp = Blueprint('music_bp', __name__, template_folder = "templates", static_folder = "static", url_prefix= "/music")

@music_bp.route("/music_bp")
def music():
    return render_template("music_bp.html")