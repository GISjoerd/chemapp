Chemapp
Map Application
This project is a Flask web application that uses Folium and various other Python libraries to create an interactive map. The map displays geographical data from a PostgreSQL database, showcasing different events and their details.

Prerequisites
Make sure you have the following installed:

Python
Flask
Folium
Shapely
psycopg2 (for PostgreSQL database connection)
You can install the required packages using the following command:

bash
Copy code
pip install Flask folium shapely psycopg2
How to Run
Clone the repository:

bash
Copy code
git clone https://github.com/your-username/your-repo.git
Navigate to the project directory:

bash
Copy code
cd your-repo
Run the Flask application:

bash
Copy code
python app.py
Open your web browser and go to http://127.0.0.1:5000/map/map_bp to view the interactive map.

Project Structure
app.py: Main application file containing Flask setup and route for the map page.
database/view.py: Module for handling database connections and queries.
templates/map_bp.html: HTML template for the map page.
static/: Folder containing static files such as CSS and JavaScript.
the-netherlands.geojson: GeoJSON file containing geographical data for the Netherlands.
Features
Interactive map displaying events with markers.
Choropleth layer displaying the outline of the Netherlands.
Clustered markers for improved map readability.
Popups with event details, including a SoundCloud player and additional information.
Links to an info page for more details about each event.
Database Setup
Set up a PostgreSQL database.
Update the database connection details in database/view.py.
Create a table named show with appropriate columns.
Customization
Adjust the map center coordinates, zoom level, and other parameters in app.py.
Customize the HTML content of popups in the map function.
Feel free to customize the code to fit your specific needs and requirements. For any issues or improvements, please open an issue or submit a pull request.

Happy mapping! 🗺️
