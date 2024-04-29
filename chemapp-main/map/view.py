from shapely.wkt import loads  
from flask import Blueprint, render_template, url_for, current_app
from database.view import get_db_connection

map_bp = Blueprint('map_bp', __name__, template_folder = "templates", static_folder = "static", url_prefix = "/map") 

@map_bp.route("/map_bp")
def map():
    #Execute a SQL query to retrive the data from database
    conn= get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, date, ST_AsText(geometry) FROM show")  # Assuming geometry is stored in a column named 'geometry'
    #creatingting shows to use later in code
    shows = cur.fetchall()
    
    # Process geometry field to get latitude and longitude
    for idx, row in enumerate(shows):
        geometry_wkt = row[3]
        point = loads(geometry_wkt)
        lat, lon = point.y, point.x
        shows[idx] = row[:3] + (lat, lon) + row[4:]  # Replace geometry with lat, lon

    cur.close()
    conn.close()
        # Using JavaScript function to handle opening hyperlink to another page
        #javascript_openpage_function = '''
           # <script>
        #        function openPage(url) {
         #           window.location.href = url;
                #}
          #  </script>
       # '''
            

      #  html+= javascript_openpage_function
    print(shows)
    return render_template("map_bp.html", shows=shows)
 