from flask import Flask, render_template, request, session, flash, redirect, url_for
from home.view import home_bp
from map.view import map_bp
from music.view import music_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(home_bp)
    app.register_blueprint(map_bp)
    app.register_blueprint(music_bp)

    return app