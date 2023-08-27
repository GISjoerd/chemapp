from flask import Blueprint, render_template

mail_bp = Blueprint('music_bp', __name__, template_folder = "templates", static_folder = "static", url_prefix= "/mail")

@mail_bp.route("/mail_bp")
def mail():
    return render_template("mail_bp.html")

