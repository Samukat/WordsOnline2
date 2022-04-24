from app import app, api, encoder
import json
import os
import datetime
#from api import get_words

from flask import make_response, render_template, redirect, request, url_for, session, jsonify, send_from_directory



@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        req = request.form
        if "ch" in req:
            requested_channel = req['ch'] #or req.get('ch'), or request.form["ch"]
            words_result = api.get_words(ch_name=requested_channel, viewPass=req['ps'], editPass=req['ps'])

            if (req['ps']) != "":
                session['lastInputedPassword'] = req['ps']
            
            if len(words_result['data']) == 0:
                return render_template("public/index.html", channel=requested_channel)

            return redirect(url_for("indexWords", enid = encoder.encode(words_result['data'][0]['id'])))
        elif "save" in req:
            print("save + " + req.get("WordsBox"))
        elif "cancel" in req:
            print("reset")
        else:
            print("Error")


    if "nonExRequested" in session:
        tmpchannel = session['nonExRequested']
        session.pop('nonExRequested')
        return render_template("public/index.html", data="", channel=tmpchannel)



    return render_template("public/viewOnly.html", data="Words Online: \nSelect channel to start")

@app.route("/<enid>", methods=["GET", "POST"])
def indexWords(enid):
    
    if request.method == "POST":
        req = request.form
        if "ch" in req:
        
            requested_channel = req['ch'] #or req.get('ch'), or request.form["ch"]
            words_result = api.get_words(ch_name=requested_channel)

            if (req['ps']) != "":
                session['lastInputedPassword'] = req['ps']

            if len(words_result['data']) == 0:

                #messages = json.dumps({"channel":requested_channel})
                session['nonExRequested'] = requested_channel
                
                return redirect(url_for('index'))

            return redirect(url_for("indexWords", enid = encoder.encode(words_result['data'][0]['id'])))

        elif "save" in req:
            print("save + " + req.get("WordsBox"))
        elif "cancel" in req:
            print("reset")
        else:
            print("Error")

    inputedPassword = None
    if 'lastInputedPassword' in session:
        inputedPassword = session['lastInputedPassword']

    words_result = api.get_words(encoded_ch_ID=enid, viewPass=inputedPassword, editPass=inputedPassword)
    if len(words_result['data']) == 0:
        return redirect(url_for('index'))

    if ('permission' in words_result['data'][0].keys()):
        if (words_result['data'][0]['permission'] == "No edit access"):
            return render_template("public/viewOnly.html", data=words_result['data'][0]['words'], channel=words_result['data'][0]['channel'])

        if (words_result['data'][0]['permission'] == "No view access"):
            return render_template("public/accessDenied.html", channel=words_result['data'][0]['channel'])
    
    if (words_result['data'][0]['viewPass'] != None and words_result['data'][0]['pass'] == None):
        return render_template("public/index.html", data=words_result['data'][0]['words'], channel=words_result['data'][0]['channel'], inputedPassword=inputedPassword, viewPass=words_result['data'][0]['viewPass'])
    if (words_result['data'][0]['viewPass'] == None and words_result['data'][0]['pass'] != None):
        return render_template("public/index.html", data=words_result['data'][0]['words'], channel=words_result['data'][0]['channel'], inputedPassword=inputedPassword, editpass=words_result['data'][0]['pass'])
    if (words_result['data'][0]['viewPass'] != None and words_result['data'][0]['pass'] != None):
        return render_template("public/index.html", data=words_result['data'][0]['words'], channel=words_result['data'][0]['channel'], inputedPassword=inputedPassword, editpass=words_result['data'][0]['pass'],viewPass=words_result['data'][0]['viewPass'])
    return render_template("public/index.html", data=words_result['data'][0]['words'], channel=words_result['data'][0]['channel'], inputedPassword=inputedPassword)


@app.route("/savedata", methods=["POST"])
def savedata():
    req = request.get_json()

    inputedPassword = None
    if 'lastInputedPassword' in session:
        inputedPassword = session['lastInputedPassword']


    result = api.save_values(ch_name=req["ch_name"], words=req["words"], newviewPass=req["newviewPass"], neweditPass=req["neweditPass"], editPass=inputedPassword, viewPass=inputedPassword)
    
    if req["neweditPass"] == "" and req["newviewPass"] != "":
        session['lastInputedPassword'] = req["newviewPass"]
        
    else:
        session['lastInputedPassword'] = req["neweditPass"]


    try:
        res = make_response(jsonify(result), 200)
        return res
    except Exception:
        return "None received", 400


@app.route("/test")
def test():
    return "<h1 style='color: red'> TEST </h1>"

@app.route("/login")
def loginOrReg():
    return render_template("public/accounts.html")


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',mimetype='image/vnd.microsoft.icon')