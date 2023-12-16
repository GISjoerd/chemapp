from flask import Flask, render_template, flash, redirect, url_for, request
from home.view import home_bp
from map.view import map_bp
from music.view import music_bp
from mail.view import mail_bp
from database.view import database_bp

app = Flask(__name__)

app.register_blueprint(home_bp)
app.register_blueprint(map_bp)
app.register_blueprint(music_bp)
app.register_blueprint(mail_bp)
app.register_blueprint(database_bp)

if __name__ == "__main__":
    app.run(debug=True)
