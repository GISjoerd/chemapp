from flask import Blueprint, render_template
import folium

map_bp = Blueprint('map_bp', __name__, template_folder = "templates", static_folder = "static", url_prefix = "/map") 
    # route to homepage
@map_bp.route("/map_bp")
def map():
    m = folium.Map(
    # coordinaten achterhoek
        location=[52.022727853219074, 6.421852949418699],
        zoom_start=9,
     )
    
    iframe = m._repr_html_()

    return render_template("map_bp.html", iframe=iframe)



    