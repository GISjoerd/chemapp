from flask import Blueprint, render_template
from folium.plugins import MarkerCluster
import folium
import json

map_bp = Blueprint('map_bp', __name__, template_folder = "templates", static_folder = "static", url_prefix = "/map") 
    # route to homepage
@map_bp.route("/map_bp")
def map():

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


 # add gejson to map
    shows = "shows.geojson"
    

     # Read the geojson file as a dictionary
    
    with open(shows) as f:
        data = json.load(f)

      # Loop through the features in the geojson file and create markers with popups
    for feature in data["features"]:
        # Get the coordinates, name and image of each feature
        coords = feature["geometry"]["coordinates"]
        name = feature["properties"]["show"]
        img = feature["properties"]["img"]
        
        # Create an HTML string for the popup
        html = f"<h3>{name}</h3><img src='{img}' width='300' height='200'>"

        # Create an iframe object from the HTML string
        iframe = folium.IFrame(html=html, width=350, height=250)

        # Create a popup object from the iframe object
        popup = folium.Popup(iframe, max_width=350)

        # Create a marker object with the popup
        marker = folium.Marker(location=[coords[1], coords[0]], popup=popup)

        # Add the marker to the marker cluster
        marker.add_to(mc)

     # set iframe width and heigth
    m.get_root().width ="1500px"
    m.get_root().height = "800px"
    iframe = m.get_root()._repr_html_()

    return render_template("map_bp.html", iframe=iframe)
