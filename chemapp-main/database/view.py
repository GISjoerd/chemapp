
from flask import request, Blueprint 
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry
import psycopg2
import json


db = SQLAlchemy()
database_bp = Blueprint('database_bp', __name__, template_folder="templates", static_folder="static", url_prefix="/database")
   
def get_db_connection():    
    conn = psycopg2.connect(host='localhost', database='CC_shows', user='postgres', password='Spalstraat@25')
    return conn

class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(100),nullable=False)
    geometry = db.Column(Geometry('POINT'))
    link_ticket = db.Column(db.String(255),nullable=False)
    link_img = db.Column(db.String(255),nullable=False)
          
    def __repr__(self):
        return f"Show: {self.name} {self.date} {self.geometry} {self.link_ticket} {self.link_img}"
        
    def __init__(self, name, date, geometry, link_ticket, link_img):
        self.name = name
        self.date = date
        self.geometry = geometry
        self.link_ticket = link_ticket
        self.link_img = link_img

def format_show(show):
    return {
        "name": show.name,
        "id": show.id,
        "date": show.date,
        "geometry": show.geometry,
        "link_ticket": show.link_ticket,
        "link_img": show.link_img
    }

@database_bp.route('/show', methods = ['POST', 'GET'])
def create_show():
    data = request.json
    name, date, geometry, link_ticket, link_img = data['name'], data['date'], data['geometry'], data['link_ticket'], data['link_img']
    geometry_insert = json.dumps(geometry)

    conn = get_db_connection()
    cur = conn.cursor()
    sql = 'INSERT INTO public.show(name, date, geometry, link_ticket, link_img) VALUES (%s, %s, ST_GeomFromGeoJSON(%s), %s, %s)'
    cur.execute(sql, (name, date, geometry_insert, link_ticket, link_img))
    conn.commit()
    
    return "Show created successfully", 201