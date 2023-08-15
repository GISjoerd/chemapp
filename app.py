from flask import Flask, render_template, request, session, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from folium.plugins import MarkerCluster
import folium


# configure app
app = Flask(__name__)
app.secret_key = 'WRchemicalclouds'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///members.db'
db = SQLAlchemy(app)

class Member(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)

    def __init__(self, email):
        self.email = email

# Create an application context
with app.app_context():
# add database if not there
    db.create_all()

# route to homepage
@app.route("/")
def home():
    return render_template("home.html")

# route to webmap
# route to embeded iframe webmap
@app.route("/iframe")
def iframe():

    # this is the basemap
    m = folium.Map(
    # coordinaten achterhoek
        location=[52.022727853219074, 6.421852949418699],
        zoom_start=9,


        icon = CustomIcon('/static/noun-guitar-pick-19436.png',
        icon_size=(38, 95),
        icon_anchor=(22, 94),
        popup_anchor=(-3, -76),
        ))


    netherlands="the-netherlands.geojson"

    folium.Choropleth(
    geo_data=netherlands,
    fill_color="#2BB8AF",
    fill_opacity=0.5,
    line_opacity=0.1,
    ).add_to(m)

    mc = MarkerCluster(icon=icon).add_to(m)


    # Sets Tile Theme to one of:
    # Stamen Toner
    # Stamen Terrain
    # cartodbpositron
    #cartodbdark_matter
    folium.TileLayer('cartodbpositron').add_to(mc)

    # add gejson to map
    shows = "shows.geojson"
    folium.GeoJson(shows).add_to(mc)

     # set iframe width and heigth
    m.get_root().width ="2000px"
    m.get_root().heigth = "2000px"
    iframe = m.get_root()._repr_html_()

    return render_template("map.html", iframe=iframe)


@app.route("/member", methods=["GET", "POST"])
def member():

    if request.method == "POST":
        email =request.form.get("email")
        session["email"] = email

        #add new member to database
        new_member = Member(email=email)
        db.session.add(new_member)
        db.session.commit()
        flash("congrats!! You are now a member of the Chemical Cloud")
        return redirect(url_for("member"))

    if "email" in session:
       email =session["email"]
       return render_template("member.html", email=email)
    else:
        return render_template("member.html")


@app.route("/music")
def music():
    return render_template("music.html")


@app.route("/merch")
def merch():
    return render_template("merch.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port = 5000)
