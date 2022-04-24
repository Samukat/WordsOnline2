from app import app

from flask import render_template

@app.route("/api/get")
def api_get():
    return "1234"
    

@app.route("/api/refrences")
def api_refrences():
    return render_template("api/refrences.html")

@app.route("/api")
def api_home():
    return render_template("api/about.html")