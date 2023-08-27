from flask import Blueprint, render_template
import folium
from folium.plugins import MarkerCluster

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
    folium.GeoJson(shows).add_to(mc)

     # set iframe width and heigth
    m.get_root().width ="1500px"
    m.get_root().height = "800px"
    iframe = m.get_root()._repr_html_()

    return render_template("map_bp.html", iframe=iframe)
