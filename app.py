from flask import Flask, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from home.view import home_bp
from map.view import map_bp
from music.view import music_bp
from mail.view import mail_bp
from geoalchemy2 import Geometry

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Student21@localhost/Chemapp'
db = SQLAlchemy(app)
    
class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(100),nullable=False)
    geometry = db.Column(Geometry('POINT'))
          
    def __repr__(self):
        return f"Show: {self.name} {self.date}"
        
    def __init__(self, name, date):
        self.name = name
        self.date = date

app.register_blueprint(home_bp)
app.register_blueprint(map_bp)
app.register_blueprint(music_bp)
app.register_blueprint(mail_bp)

if __name__ == "__main__":
    app.run(debug=True)

