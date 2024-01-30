import folium
import json
from shapely.wkt import loads
from flask import Blueprint, render_template, url_for, current_app
from folium.plugins import MarkerCluster
from database.view import get_db_connection


map_bp = Blueprint('map_bp', __name__, template_folder = "templates", static_folder = "static", url_prefix = "/map") 



@map_bp.route("/map_bp")
def map():
    #Execute a SQL query to retrive the data from database
    conn= get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT*FROM show")
    #creatingting shows to use later in code
    shows = cur.fetchall()
    
    

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

    mc = MarkerCluster()

    # Sets Tile Theme to one of:
    # Stamen Toner
    # stamenterrain
    # cartodbpositron
    #cartodbdark_matter
    #MapQuest Open Aerial
    folium.TileLayer('cartodbdark_matter').add_to(mc)

    markers = []  # Initialize markers array to keep track of added markers
    
      # Loop through the rows in the database show
    for row in shows:
        id = row[0]
        name = row[1]
        date = row[2]
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
        html = '<iframe width="100%" height="300" scrolling="no" frameborder="no" src="https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/1731040173&color=%235474a0&auto_play=true&hide_related=false&show_comments=true&show_user=true&show_reposts=false&show_teaser=true&visual=true"></iframe><div style="font-size: 10px; color: #cccccc;line-break: anywhere;word-break: normal;overflow: hidden;white-space: nowrap;text-overflow: ellipsis; font-family: Interstate,Lucida Grande,Lucida Sans Unicode,Lucida Sans,Garuda,Verdana,Tahoma,sans-serif;font-weight: 100;"><a href="https://soundcloud.com/user-889499625" title="sjoerd" target="_blank" style="color: #cccccc; text-decoration: none;">sjoerd</a> · <a href="https://soundcloud.com/user-889499625/fjords1" title="Fjords" target="_blank" style="color: #cccccc; text-decoration: none;">Fjords</a></div><br><img src="https://www.w3schools.com/w3images/lights.jpg" alt="Lights" style="width:100%">'
        html += f"<h3>{name}</h3>"
        html += f"<h3>{date}</h3>"
        html += f"<h3>{id}</h3>"
        html += f'<img src="{url_for("static", filename="cc_resize.jpg")}" alt="band">'
        #html += f'<a href="http://127.0.0.1:5000/info_bp"onclick="openPage(\'{current_app.url_for("info_bp.info")}\')"target="_blank">info</a>'
        html += f'<a href="http://127.0.0.1:5000/info_bp" onclick="openPage(\'{current_app.url_for("info_bp.info")}\')" target="_blank">info</a>'
    
        

        # Using JavaScript function to handle opening hyperlink to another page
        javascript_openpage_function = '''
            <script>
                function openPage(url) {
                    window.location.href = url;
                }
            </script>
        '''
        html+= javascript_openpage_function
        iframe = folium.IFrame(html=html, width=350, height=250)
        popup = folium.Popup(iframe)
        #lat and long has been turend around
        marker = folium.Marker(location=[long, lat], popup=popup, custom_id=int(id))
        marker.add_to(mc)

        #creating a list of show (events) using html+javascript
        markers.append(marker)  # Add the marker to the markers array

    mc.add_to(m) #add the mc to main map
    

     # set iframe width and heigth
    m.get_root().width ="1000px"
    m.get_root().height = "650px"
    iframe = m.get_root()._repr_html_()
    print(shows)
    print(markers)
   
    cur.close()
    conn.close()
    return render_template("map_bp.html", iframe=iframe, shows=shows, lat=lat, long=long, markers = markers)
 