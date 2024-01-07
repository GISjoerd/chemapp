
from flask import Flask, request, Blueprint
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry
import psycopg2
import json

database_bp = Blueprint('database_bp', __name__, template_folder="templates", static_folder="static", url_prefix="/database")

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Spalstraat%4025@localhost/CC_shows'
db = SQLAlchemy(app)
    
def get_db_connection():    
    conn = psycopg2.connect(host='localhost', database='CC_shows', user='postgres', password='Spalstraat@25')
    return conn

class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(100),nullable=False)
    geometry = db.Column(Geometry('POINT'))
          
    def __repr__(self):
        return f"Show: {self.name} {self.date} {self.geometry}"
        
    def __init__(self, name, date, geometry):
        self.name = name
        self.date = date
        self.geometry = geometry

def format_show(show):
    return {
        "name": show.name,
        "id": show.id,
        "date": show.date,
        "geometry": show.geometry
    }

@app.route('/show', methods = ['POST'])
def create_show():
    data = request.json
    name, date, geometry = data['name'], data['date'], data['geometry']
    geometry_insert = json.dumps(geometry)

    conn = get_db_connection()
    cur = conn.cursor()
    sql = 'INSERT INTO public.show(name, date, geometry) VALUES (%s, %s, ST_GeomFromGeoJSON(%s))'
    cur.execute(sql, (name, date, geometry_insert))
    conn.commit()

    # Create tables within the context of the application
with app.app_context():
    db.create_all()