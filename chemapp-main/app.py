from flask import Flask, render_template, flash, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from home.view import home_bp
from about.view import about_bp
from map.view import map_bp
from info.view import info_bp
from music.view import music_bp
from mail.view import mail_bp
from database.view import database_bp

 

app = Flask(__name__)   
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Spalstraat%4025@localhost/CC_shows'
db = SQLAlchemy(app)

def create_tables():
    with app.app_context():
        db.create_all()

# Call the function to create tables before the first request
create_tables()

#register blueprints
app.register_blueprint(home_bp)
app.register_blueprint(about_bp)
app.register_blueprint(map_bp)
app.register_blueprint(info_bp)
app.register_blueprint(music_bp)
app.register_blueprint(mail_bp)
app.register_blueprint(database_bp)

if __name__ == "__main__":
    app.run(debug=True)