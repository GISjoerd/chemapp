import folium
import json
from shapely.wkt import loads
from flask import Blueprint, render_template
from folium.plugins import MarkerCluster
from database.view import get_db_connection

map_bp = Blueprint('map_bp', __name__, template_folder = "templates", static_folder = "static", url_prefix = "/map") 
    # route to homepage


@map_bp.route("/map_bp")
def map():
    #Execute a SQL query to retrive the data from database
    conn= get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT*FROM show")

    m = folium.Map(
    # coordinaten achterhoek
        location=[52.022727853219074, 6.421852949418699],
        zoom_start=6,
    )

    netherlands="the-netherlands.geojson"

    folium.Choropleth(
    geo_data=netherlands,
    fill_color="#FFFFFF",
    line_color="#000000",
    fill_opacity=0.7,
    line_opacity=0.5,
    ).add_to(m)

    mc = MarkerCluster().add_to(m)

    # Sets Tile Theme to one of:
    # Stamen Toner
    # Stamen Terrain
    # cartodbpositron
    #cartodbdark_matter
    #MapQuest Open Aerial
    folium.TileLayer('cartodbdark_matter').add_to(mc)

    
      # Loop through the rows in the database show
    for row in cur.fetchall():
        name = row[1]
        geometry = row[3]

        #Convert binary geometry to WKT using ST_AsText in SQL
        cur.execute("SELECT ST_AsText(%s)", (geometry,))
        wkt_result= cur.fetchone()
        if wkt_result:
            geometry_wkt = wkt_result[0]
            point =loads(geometry_wkt)

            lat, long = point.xy

            lat = lat[0]
            long = long[0]

        # Create an HTML string for the popup
        html = f"<h3>{name}</h3>" 
        iframe = folium.IFrame(html=html, width=350, height=250)
        popup = folium.Popup(iframe, max_width=350)
        
        #lat and long has been turend around
        marker = folium.Marker(location=[long, lat], popup=popup)
        marker.add_to(mc)

     # set iframe width and heigth
    m.get_root().width ="1500px"
    m.get_root().height = "800px"
    iframe = m.get_root()._repr_html_()

    cur.close()
    conn.close()

    return render_template("map_bp.html", iframe=iframe)
